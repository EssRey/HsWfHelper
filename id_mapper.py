import json

###
# Configuration
###

with open("id_mappings.json", "r") as read_file:
    id_mappings = json.load(read_file)

###
# Getter functions
###

def get_workflowId(obj_id):
    # WORKFLOW_ENROLLMENT
    if obj_id in id_mappings["workflowId"]["map"]:
        obj_id = id_mappings["workflowId"]["map"]["id"]
    elif id_mappings["workflowId"]["fallback"]:
        obj_id = id_mappings["workflowId"]["fallback"]
    return obj_id

def get_emailContentId(obj_id):
    # NOTIFICATION, EMAIL
    if obj_id in id_mappings["emailContentId"]["map"]:
        obj_id = id_mappings["emailContentId"]["map"]["id"]
    elif id_mappings["emailContentId"]["fallback"]:
        obj_id = id_mappings["emailContentId"]["fallback"]
    return obj_id

def get_userId(obj_id):
    # SMS_NOTIFICATION
    if obj_id in id_mappings["userId"]["map"]:
        obj_id = id_mappings["userId"]["map"]["id"]
    elif id_mappings["userId"]["fallback"]:
        obj_id = id_mappings["userId"]["fallback"]
    return obj_id

def get_teamId(obj_id):
    # LEAD_ASSIGNMENT
    if obj_id is None:
        return obj_id
    elif obj_id in id_mappings["teamId"]["map"]:
        obj_id = id_mappings["teamId"]["map"]["id"]
    elif id_mappings["teamId"]["fallback"]:
        obj_id = id_mappings["teamId"]["fallback"]
    # is either None or single-valued
    return obj_id

def get_ownerId(obj_id):
    # DEAL, TASK
    if obj_id in id_mappings["ownerId"]["map"]:
        obj_id = id_mappings["ownerId"]["map"]["id"]
    elif id_mappings["ownerId"]["fallback"]:
        obj_id = id_mappings["ownerId"]["fallback"]
    return obj_id

def get_listId(obj_id):
    # UPDATE_LIST
    if obj_id in id_mappings["workflowId"]["map"]:
        obj_id = id_mappings["workflowId"]["map"]["id"]
    elif id_mappings["workflowId"]["fallback"]:
        obj_id = id_mappings["workflowId"]["fallback"]
    return obj_id

def get_subscriptionId(obj_id):
    # UPDATE_EMAIL_SUBSCRIPTION
    if obj_id in id_mappings["subscriptionId"]["map"]:
        obj_id = id_mappings["subscriptionId"]["map"]["id"]
    elif id_mappings["subscriptionId"]["fallback"]:
        obj_id = id_mappings["subscriptionId"]["fallback"]
    return obj_id

def get_recipientUserIds(id_list):
    # NOTIFICATION_STATION
    id_list_copy = []
    if isinstance(id_list, list):
        for obj_id in id_list:
            id_list_copy.append(get_userId(obj_id))
        return id_list_copy
    return id_list

def get_recipientTeamIds(id_list):
    # NOTIFICATION_STATION
    id_list_copy = []
    if isinstance(id_list, list):
        for obj_id in id_list:
            id_list_copy.append(get_teamId(obj_id))
        return id_list_copy
    return id_list

def get_owners(id_list):
    # LEAD_ASSIGNMENT
    id_list_copy = []
    if isinstance(id_list, list):
        for obj_id in id_list:
            id_list_copy.append(get_ownerId(obj_id))
        return id_list_copy
    return id_list

def get_filters(filters):
    # BRANCH
    dummy_filter = """
    [
        [
            {
                "operator": "IS_NOT_EMPTY",
                "filterFamily": "PropertyValue",
                "withinTimeMode": "PAST",
                "type": "datetime",
                "property": "createdate"
            }
        ]
    ]
    """
    return json.loads(dummy_filter)

attribute_to_getter = {
    "workflowId": get_workflowId,
    "emailContentId": get_emailContentId,
    "userId": get_userId,
    "ownerId": get_ownerId,
    "teamId": get_teamId,
    "listId": get_listId,
    "subscriptionId": get_subscriptionId,
    "recipientUserIds": get_recipientUserIds,
    "recipientTeamIds": get_recipientTeamIds,
    "owners": get_owners,
    "filters": get_filters
}

###
# External interface
###

def get_target_id(attribute, value_origin):
    # will look up the mapping in id_mappings.json
    # if there is no mapping it will apply any fallback value provided
    # if there is no mapping and no fallback, it RETURNS THE ORIGINAL VALUE
    # (remove mappings and fallback if an ID should not be changed)
    return attribute_to_getter[attribute](value_origin)
