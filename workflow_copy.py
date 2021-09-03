#-------------
# Imports
#-------------
import requests, json
from dotenv import dotenv_values
from id_mapper import get_target_id
from wf_key_mapper import get_wf_key_value
import time
#from segment_parser import get_log

#-------------
# Configuration
#-------------

config = dotenv_values(".env")
hapikey_origin = config["HAPIKEY_ORIGIN"]
hapikey_target = config["HAPIKEY_TARGET"]
with open("action_schemata.json", "r") as read_file:
    action_schemata = json.load(read_file)
with open("reference_properties.json", "r") as read_file:
    reference_properties = json.load(read_file)
# note that the ID mappings (currently as stub) is managed in the id_mapper.py module; TO DO streamline config
with open("wf_schema.json", "r") as read_file:
    wf_schema = json.load(read_file)

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
             "propertyName": "message",
             "newValue": json.dumps(placeholder_content)
             }
    #if "anchorSetting" in placeholder_content:
    #    pass
    #    placeholder_node["anchorSetting"] = placeholder_content["anchorSetting"]
    return placeholder_node

#-------------
# Action processor function
#-------------

# TO DO auto-creation of "flag" (annotation) nodes

def apply_schema(node):
    if node["type"] not in action_schemata:
        print("Warning: unknown action " + str(node["type"]))
        return [create_placeholder(node)]
    schema = action_schemata[node["type"]]
    node_copy = {}
    for attribute in node:
        if schema[attribute]=="NOT_IMPLEMENTED":
            return [create_placeholder(node)]
        elif schema[attribute]=="PASS":
            node_copy[attribute] = node[attribute]
        elif schema[attribute]=="SUBSTITUTE":
            if node[attribute] is None:
                node_copy[attribute] = None
            else:
                substitution_result = get_target_id(attribute, node[attribute])
                if substitution_result is None:
                    return [create_placeholder(node)]
                else:
                    node_copy[attribute] = substitution_result
    # special cases
    def ambiguous_prop(prop):
        obj_with_prop = [obj for obj in reference_properties if prop in reference_properties[obj]]
        return obj_with_prop != ["company"]
    ## identify "delay until time of day or day of the week" actions
    if node_copy["type"] == "DELAY" and node_copy["delayMillis"] == 0 and "anchorSetting" not in node_copy:
        return [create_placeholder(node_copy)]
    ## identify set/copy property actions with a property that cannot be uniquely matched to contact or company
    elif node_copy["type"] == "SET_COMPANY_PROPERTY":
        if ambiguous_prop(node_copy["propertyName"]):
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "COPY_PROPERTY" and node_copy["targetModel"] == "COMPANY":
        if ambiguous_prop(node_copy["targetProperty"]):
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "DATE_STAMP_PROPERTY" and node_copy["model"] == "COMPANY":
        if ambiguous_prop(node_copy["targetProperty"]):
            return [create_placeholder(node_copy)]
    elif node_copy["type"] == "ADD_COMPANY_ENUM_PROPERTY":
        if ambiguous_prop(node_copy["propertyName"]):
            return [create_placeholder(node_copy)]
    ## flag possibly missing team IDs in the lead rotation action
    elif node_copy["type"] == "LEAD_ASSIGNMENT" and node_copy["teamId"] is not None:
        return [create_placeholder("TODO: check for missing Teams selected in following lead roation action."), node_copy]
    ## unassigned tasks now possible via UI, but API will error out
    elif node_copy["type"] == "TASK" and node_copy["ownerId"] is None and node_copy["ownerProperty"] is None:
        return [create_placeholder(node_copy)]
    ## any owner recipient in the "Send in-app notification" action need to be checked manually
    elif node_copy["type"] == "NOTIFICATION_STATION":
        if node_copy["recipientUserIds"] == [] and node_copy["recipientTeamIds"] == []:
            return [create_placeholder(node)]
        else:
            return [create_placeholder("TODO: check for missing owner recipients in following notification action."), node_copy]
    # may have to consider "create ticket" and "create deal" actions here in future
    return [node_copy]

#-------------
# Graph traversal function 
# (recursive version)
# (this relies on list copies in order to facilitate element insertion during iteration)
#-------------

def process_actions(actions, node_processor):
# takes and returns a list of actions
# node_processor must take an action (dict) and return a list of actions
    action_list = []
    for action in actions:
        if action["type"]=="BRANCH":
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
    try:
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
    except:
        print("crazy retry pause starts")
        time.sleep(10)
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
    actions = process_actions(workflow["actions"], apply_schema)
    target_workflow = {
        "actions": actions
    }
    for key in workflow:
        if key not in wf_schema:
            print("[Warning] Unknown workflow key: " + str(key) + " (skip and proceed)")
        else:
            if wf_schema[key]=="SUBSTITUTE":
                target_workflow[key] = get_wf_key_value(key, workflow[key])
            elif wf_schema[key]=="PASS":
                target_workflow[key] = workflow[key]
    return target_workflow


def copy_workflow(workflow_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=False, prefix="", simulate=False):
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
        print(workflow_id)
        #print ("Workflow " + str(workflow_id) + " was not copied.")
        with open("playground/logs/wf_v7_"+str(workflow_id)+"_"+str(r.status_code)+".json", "w") as data_file:
            json.dump(r.json(), data_file, indent=2)
    elif not silent:
        pass
        #print ("Workflow " + str(workflow_id) + " successfully copied.")
    return r

def copy_all_workflows(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=True, prefix="TESTCOPY_", simulate=False):
    all_workflows = requests.get(url_wf_all(hapikey_origin)).json()["workflows"]
    for workflow in all_workflows:
        workflow_id = workflow["id"]
        newId = workflow["migrationStatus"]["flowId"]
        r = copy_workflow(workflow_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=silent, prefix=prefix, simulate=simulate)
        # log the http response
        #with open("playground/logs/"+str(r.status_code)+"__"+str(newId)+"_"+str(workflow_id)+".json", "w") as data_file:
        #    json.dump(r.json(), data_file, indent=2)

#temporary convenience function (for testing and inspection)
def dump_all_workflows(hapikey_origin=hapikey_origin):
    wf_list=[]
    wf_key_set=set()
    all_workflows = requests.get(url_wf_all(hapikey_origin)).json()["workflows"]
    print(len(all_workflows))
    for workflow in all_workflows:
        workflow_id = workflow["id"]
        workflow = requests.get(url_wf(str(workflow_id), hapikey_origin)).json()
        wf_keys=set(workflow.keys())
        wf_key_set=wf_key_set.union(wf_keys)
        workflow["actions"]=[]
        wf_list.append(workflow)
    print(len(wf_list))
    with open("playground/logs/non_drip_workflows_dump.json", "w") as f:
        for wf in wf_list:
            f.write("%s\n" % wf)
    print(wf_key_set)

if __name__ == "__main__":
    #copy_all_workflows(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=False, simulate=False)
    #for w_id in [2382774,2532410,2532466,2564776,3061268,3061274,3380420,3685474,4754778,4762765,5991996,6531825,6647332,6647334,6727626,6743897,6781224,6978233,7097420,7854920,9533603,26949206]:
    #    copy_workflow(w_id, silent=False, simulate=False)
    dump_all_workflows()
    #get_log()