#-------------
# Imports
#-------------
import requests
from dotenv import dotenv_values


#-------------
# Configuration
#-------------

config = dotenv_values(".env")
hapikey_origin = config["HAPIKEY_ORIGIN"]
hapikey_target = config["HAPIKEY_TARGET"]

# this is a dictionary of all action schemata; the exact structure will probably change
schemata = {"DELAY": [
    "type",
    "delayMillis",
    "stepId",
    "anchorSetting",
    "actionId"
],
    "SET_CONTACT_PROPERTY": [
        "newValue",
        "type",
        "propertyName"
],
    "BRANCH": [
        "type",
        "filters",
        "rejectActions",
        "acceptActions"
]}

# dictionary-of-dictionaries. Each top-level key corresponds to an action attribute, and each value is a map of IDs
mappings = {"ownerId": {"123": "456", "124": "789"}, "listId": {"1": "123"}}

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
# dummy getters
#-------------
def get_dummy_node(message):
    dummy = {"type": "SET_CONTACT_PROPERTY",
             "propertyName": "message",
             "newValue": message
             }
    return dummy

def get_dummy_branch(node):
    node["filters"] = [
        [
            {
                "operator": "EQ",
                "withinTimeMode": "PAST",
                "filterFamily": "PropertyValue",
                "type": "string",
                "property": "message",
                "value": "PLACEHOLDER_CONDITION"
            }
        ]
    ]
    return node

#-------------
# Action processor functions
# (mostly stubs or partial dummies)
# (note some inconsistency: return action or list of actions)
#-------------

def validate_node(node):
    # not implemented yet
    return [node]

def substitute_ids(node):
    # minimal implementation (skips non-existing keys, surfaces no errors)
    for key in node:
        try:
            node[key]=mappings[key][node[key]]
        except KeyError:
            pass
        except:
            print(node)
    return [node]

def cull_node(node):
    # proof-of-concept for two node types
    if node["type"]=="BRANCH":
        return [{ key: node[key] for key in schemata["BRANCH"] }]
    elif node["type"]=="SET_CONTACT_PROPERTY":
        return [{ key: node[key] for key in schemata["SET_CONTACT_PROPERTY"] }]
    else:
        return [dummy_processor(node)]

# this is a composite node processing function -- I will probably refactor to avoid this sort of thing
def dummy_processor(node):
    node = validate_node(node)[0]
    node = substitute_ids(node)[0]
    if node["type"]=="BRANCH":
        return [get_dummy_node("CHECK MISSING BRANCHES"), get_dummy_branch(node)]
    else:
        return [get_dummy_node("[placeholder for " + str(node["type"]) + " action]")]

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
    id = workflow["id"]
    newId = workflow["migrationStatus"]["flowId"]
    name = workflow["name"]
    actions = requests.get(url_wf(id, hapikey_origin)).json()["actions"]
    # apply processing steps to the actions graph
    actions = process_actions(actions, dummy_processor)
    actions = process_actions(actions, cull_node)
    # write workflow to target portal
    url_create_wf(hapikey_target)
    body = {
        "name": "[DUMMY-MIGRATED]_" + name,
        "type": type,
        "onlyEnrollsManually": True,
        "actions": actions
    }
    r = requests.post(url_create_wf(hapikey_target), json = body)
    if not r:
        print(r.text)
        print ("Workflow " + str(newId) + " was not copied.")