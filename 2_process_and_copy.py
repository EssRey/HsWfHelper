#-------------
# Imports
#-------------
import requests, json
from dotenv import dotenv_values
from id_mapper import get_target_id

#-------------
# Configuration
#-------------

config = dotenv_values(".env")
hapikey_origin = config["HAPIKEY_ORIGIN"]
hapikey_target = config["HAPIKEY_TARGET"]
with open("action_schemata.json", "r") as read_file:
    action_schemata = json.load(read_file)
# note that the ID mappings (currently as stub) is managed in the id_mapper.py module; TO DO streamline config

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
    return placeholder_node

#-------------
# Action processor function
#-------------

# TO DO auto-creation of "flag" (annotation) nodes

def apply_schema(node):
    if node["type"] in action_schemata:
        schema = action_schemata[node["type"]]
        node_copy = {}
        for attribute in node:
            if schema[attribute]=="NOT_IMPLEMENTED":
                return [create_placeholder(node)]
            elif schema[attribute]=="PASS":
                node_copy[attribute] = node[attribute]
            elif schema[attribute]=="SUBSTITUTE":
                node_copy[attribute] = get_target_id(attribute, node[attribute])
        return [node_copy]
    else: 
        return [create_placeholder(node)]

#-------------
# Graph traversal function 
# (recursive version)
# (this relies on list copies in order to facilitate element insertion during iteration)
#-------------

def process_actions(actions, node_processor):
# takes and returns a list of nodes
# node_processor must take an action (dict) and return a list of actions (list of dicts)
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
# EXECUTION
# read all workflows, loop over them, process each and write it to target portal
#-------------

all_workflows = requests.get(url_wf_all(hapikey_origin)).json()["workflows"]
for workflow in all_workflows:
    type = workflow["type"]
    name = workflow["name"]
    id = workflow["id"]
    newId = workflow["migrationStatus"]["flowId"]
    actions = requests.get(url_wf(id, hapikey_origin)).json()["actions"]
    # apply processing steps to the actions graph
    actions = process_actions(actions, apply_schema)
    # write workflow to target portal
    url_create_wf(hapikey_target)
    body = {
        "name": "[MIGRATED_v2]_" + name,
        "type": type,
        "onlyEnrollsManually": True,
        "actions": actions
    }
    r = requests.post(url_create_wf(hapikey_target), json = body)
    if not r:
        print(r.text)
        print ("Workflow " + str(newId) + " was not copied.")
    # log the http response
    with open("playground/logs/"+str(r.status_code)+"__"+str(newId)+"_"+str(id)+".json", "w") as data_file:
        json.dump(r.json(), data_file, indent=2)