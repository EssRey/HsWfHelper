#-------------
# Imports
#-------------
import requests, json
#from dotenv import dotenv_values
from id_mapper import get_target_id
from wf_key_mapper import get_wf_key_value
import time
from segment_parser import parse_segments
#from segment_parser import get_log
import config
import logger

#-------------
# Configuration
#-------------

action_placeholder_property = config.action_placeholder_property

#config = dotenv_values(".env")
hapikey_origin = config.hapikey_origin #config["HAPIKEY_ORIGIN"]
hapikey_target = config.hapikey_target #config["HAPIKEY_TARGET"]

action_schemata = config.action_schemata
reference_properties = config.reference_properties
wf_schema = config.wf_schema

#-------------
# URL getters
#-------------
def url_wf(workflowId, hapikey):
    return "https://api.hubapi.com/automation/v3/workflows/" + str(workflowId) + "?hapikey=" + hapikey
def url_wf_all(hapikey):
    return "https://api.hubapi.com/automation/v3/workflows?hapikey=" + hapikey
def url_create_wf(hapikey):
    return "https://api.hubapi.com/automation/v3/workflows?hapikey=" + hapikey

#-------------
# Placeholder creator function
#-------------
def create_placeholder(placeholder_content):
    placeholder_node = {"type": "SET_CONTACT_PROPERTY",
             "propertyName": action_placeholder_property,
             "newValue": json.dumps(placeholder_content)
             }
    #if "anchorSetting" in placeholder_content:
    #    pass
    #    placeholder_node["anchorSetting"] = placeholder_content["anchorSetting"]
    return placeholder_node

#-------------
# Action processor function
#-------------

def apply_schema(node):
    if node["type"] not in action_schemata:
        print("Warning: unknown action " + str(node["type"]))
        logger.log_event("placeholder_action", {"type": node["type"]})
        return [create_placeholder(node)]
    schema = action_schemata[node["type"]]
    node_copy = {}
    for attribute in node:
        if schema[attribute]=="NOT_IMPLEMENTED":
            logger.log_event("placeholder_action", {"type": node["type"]})
            return [create_placeholder(node)]
        elif schema[attribute]=="PASS":
            node_copy[attribute] = node[attribute]
        elif schema[attribute]=="PARSE_SEGMENTS":
            #print(node[attribute])
            node_copy[attribute] = parse_segments(node[attribute])
        elif schema[attribute]=="SUBSTITUTE":
            if node[attribute] is None:
                node_copy[attribute] = None
            else:
                substitution_result = get_target_id(attribute, node[attribute])
                if substitution_result is None:
                    logger.log_event("placeholder_action", {"type": node["type"]})
                    return [create_placeholder(node_copy)]
                else:
                    node_copy[attribute] = substitution_result
    # special cases
    def ambiguous_prop(prop):
        obj_with_prop = [obj for obj in reference_properties if prop in reference_properties[obj]]
        return obj_with_prop != ["company"]
    ## identify "delay until time of day or day of the week" actions
    if node_copy["type"] == "DELAY" and node_copy["delayMillis"] == 0 and "anchorSetting" not in node_copy:
        logger.log_event("placeholder_action", {"type": node_copy["type"]})
        return [create_placeholder(node_copy)]
    ## identify set/copy property actions with a property that cannot be uniquely matched to contact or company
    elif node_copy["type"] == "SET_COMPANY_PROPERTY":
        if ambiguous_prop(node_copy["propertyName"]):
            logger.log_event("placeholder_action", {"type": node_copy["type"]})
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "COPY_PROPERTY" and node_copy["targetModel"] == "COMPANY":
        if ambiguous_prop(node_copy["targetProperty"]):
            logger.log_event("placeholder_action", {"type": node_copy["type"]})
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "DATE_STAMP_PROPERTY" and node_copy["model"] == "COMPANY":
        if ambiguous_prop(node_copy["targetProperty"]):
            logger.log_event("placeholder_action", {"type": node_copy["type"]})
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "ADD_COMPANY_ENUM_PROPERTY":
        if ambiguous_prop(node_copy["propertyName"]):
            logger.log_event("placeholder_action", {"type": node_copy["type"]})
            return [create_placeholder(node_copy)]
    ## flag possibly missing team IDs in the lead rotation action
    elif node_copy["type"] == "LEAD_ASSIGNMENT" and node_copy["teamId"] is not None:
        logger.log_event("todo_action", {"type": node_copy["type"]})
        return [create_placeholder("TODO: check for missing Teams selected in following lead roation action."), node_copy]
    ## unassigned tasks now possible via UI, but API will error out
    elif node_copy["type"] == "TASK" and node_copy["ownerId"] is None and node_copy["ownerProperty"] is None:
        logger.log_event("placeholder_action", {"type": node_copy["type"]})
        return [create_placeholder(node_copy)]
    ## any owner recipient in the "Send in-app notification" action need to be checked manually
    elif node_copy["type"] == "NOTIFICATION_STATION":
        if node_copy["recipientUserIds"] == [] and node_copy["recipientTeamIds"] == []:
            logger.log_event("placeholder_action", {"type": node_copy["type"]})
            return [create_placeholder(node)]
        else:
            logger.log_event("todo_action", {"type": node_copy["type"]})
            return [create_placeholder("TODO: check for missing owner recipients in following notification action."), node_copy]
    # may have to consider "create ticket" and "create deal" actions here in future
    # double-check types
    for key_origin in node:
        if key_origin in node_copy:
            if type(node[key_origin]) != type(node_copy[key_origin]):
                raise TypeError(str(logger.object_type)+"_"+str(logger.object_id) + " " + str(key_origin) + " type discrepancy:")
                #print(str(logger.object_type)+"_"+str(logger.object_id) + " " + str(key_origin) + " type discrepancy:")
                #print(node)
                #print(node_copy)
    return [node_copy]

#-------------
# Graph traversal function 
# (recursive version)
# (relies on list copies in order to facilitate element insertion during iteration)
#-------------

def process_actions(actions, node_processor):
# takes and returns a list of actions
# node_processor must take an action (dict) and return a list of actions
    action_list = []
    logger.set_segment_context("branching")
    for action in actions:
        if action["type"]=="WORKFLOW_ENROLLMENT":
            logger.log_event("action_dependency", {"workflowId": str(action["workflowId"])})
        if action["type"]=="BRANCH":
            logger.log_event("branching_action")
            branch_node = action.copy()
            branch_node["rejectActions"] = process_actions(action["rejectActions"], node_processor)
            branch_node["acceptActions"] = process_actions(action["acceptActions"], node_processor)
            action_list.extend(node_processor(branch_node))
        else:
            action_list.extend(node_processor(action))
    return action_list

#-------------
# Workflow copy functions
#-------------

def process_workflow(workflow_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=False):
    logger.set_logging_object("workflow", workflow_id)
    try:
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
    except:
        print("crazy retry pause starts")
        time.sleep(10)
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
    actions = process_actions(workflow["actions"], apply_schema)
    # short circuit action
    actions = [
        {
            "type": "BRANCH",
            "filters": [
                [
                    {
                        "operator": "IS_EMPTY",
                        "filterFamily": "PropertyValue",
                        "withinTimeMode": "PAST",
                        "property": "createdate",
                        "type": "datetime"
                    }
                ]
            ],
            "rejectActions": [],
            "acceptActions": actions
        }
    ]
    target_workflow = {
        "actions": actions
    }
    for key in workflow:
        if key not in wf_schema:
            print("[Warning] Unknown workflow key: " + str(key) + " (skip and proceed)")
        else:
            if wf_schema[key]=="SUBSTITUTE":

                target_workflow[key] = get_wf_key_value(key, workflow[key])
                # short-circuit enrollment condition
                if key == "segmentCriteria":
                    additional_trigger = [
                        {
                            "operator": "CONTAINS",
                            "filterFamily": "PropertyValue",
                            "withinTimeMode": "PAST",
                            "property": "message",
                            "value": str(workflow_id),
                            "type": "string"
                        }
                    ]
                    target_workflow[key].append(additional_trigger)
                    #print(target_workflow[key])
                    #target_workflow[key].append(additional_trigger)
                    #print(test)
            elif wf_schema[key]=="PASS":
                target_workflow[key] = workflow[key]
#    print(workflow.keys())
#    print(target_workflow)
    return target_workflow


def copy_workflow(workflow_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=False, simulate=False):
    #workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
    #print(workflow)
    #wf_type = workflow["type"]
    #name = workflow["name"]
    #newId = workflow["migrationStatus"]["flowId"]
    #actions = process_actions(workflow["actions"], apply_schema)
    #body = {
    #    "name": str(prefix) + name,
    #    "type": wf_type,
    #    "onlyEnrollsManually": True,
    #    "actions": actions
    #}
    # print(body)
    body = process_workflow(workflow_id)
    if simulate:
        r = {"text": "not really doing anything"}
        silent = True
    else:
        r = requests.post(url_create_wf(hapikey_target), json = body)
    if not r and not silent:
        #print(r.text)
        print("Workflow " + str(workflow_id) + " could not be copied (Error " + str(r.status_code) +", see log subdirectory for full http response).")
        with open("playground/logs/wf_REAL_v14_"+str(workflow_id)+"_"+str(r.status_code)+".json", "w") as data_file:
            json.dump(r.json(), data_file, indent=2)
    elif not silent:
        print ("Workflow " + str(workflow_id) + " successfully copied.")
    return r

def copy_all_workflows(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=True, simulate=False):
    all_workflows = requests.get(url_wf_all(hapikey_origin)).json()["workflows"]
    for workflow in all_workflows:
        workflow_id = workflow["id"]
        newId = workflow["migrationStatus"]["flowId"]
        r = copy_workflow(workflow_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=silent, simulate=simulate)
        # log the http response
        #with open("playground/logs/"+str(r.status_code)+"__"+str(newId)+"_"+str(workflow_id)+".json", "w") as data_file:
        #    json.dump(r.json(), data_file, indent=2)

#temporary convenience function (for testing and inspection)
def dump_all_workflows(hapikey_origin=hapikey_origin, portal_identifier="TEST"):
    wf_list=[]
    #wf_key_set=set()
    all_workflows = requests.get(url_wf_all(hapikey_origin)).json()["workflows"]
    print(len(all_workflows))
    for workflow in all_workflows:
        workflow_id = workflow["id"]
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
        #wf_keys=set(workflow.keys())
        #wf_key_set=wf_key_set.union(wf_keys)
        #workflow["actions"]=[]
        wf_list.append(workflow)
    print(len(wf_list))
    with open("playground/logs/"+portal_identifier+"_all_workflows.txt", "w") as f:
        for wf in wf_list:
            f.write("%s\n" % wf)
    #print(wf_key_set)

if __name__ == "__main__":
    #dump_all_workflows(hapikey_origin="hapikey", portal_identifier="CUSTOMER")
    copy_all_workflows(simulate=True)
    #logger.write_log("my_log")
