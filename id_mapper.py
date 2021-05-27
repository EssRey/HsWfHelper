import json

###
# Configuration
###

with open("id_mappings.json", "r") as read_file:
    id_mappings = json.load(read_file)

###
# Getter functions
###

def get_workflowId(id):
    # WORKFLOW_ENROLLMENT
    if id in id_mappings["workflowId"]["map"]:
        id = id_mappings["workflowId"]["map"]["id"]
    elif id_mappings["workflowId"]["fallback"]:
        id = id_mappings["workflowId"]["fallback"]
    return id

def get_emailContentId(id):
    # NOTIFICATION, EMAIL
    if id in id_mappings["emailContentId"]["map"]:
        id = id_mappings["emailContentId"]["map"]["id"]
    elif id_mappings["emailContentId"]["fallback"]:
        id = id_mappings["emailContentId"]["fallback"]
    return id

def get_userId(id):
    # SMS_NOTIFICATION
    if id in id_mappings["userId"]["map"]:
        id = id_mappings["userId"]["map"]["id"]
    elif id_mappings["userId"]["fallback"]:
        id = id_mappings["userId"]["fallback"]
    return id

def get_teamId(id):
    # LEAD_ASSIGNMENT
    if id is None:
        return id
    elif id in id_mappings["teamId"]["map"]:
        id = id_mappings["teamId"]["map"]["id"]
    elif id_mappings["teamId"]["fallback"]:
        id = id_mappings["teamId"]["fallback"]
    # is either None or single-valued
    return id

def get_ownerId(id):
    # DEAL, TASK
    if id in id_mappings["ownerId"]["map"]:
        id = id_mappings["ownerId"]["map"]["id"]
    elif id_mappings["ownerId"]["fallback"]:
        id = id_mappings["ownerId"]["fallback"]
    return id

def get_listId(id):
    # UPDATE_LIST
    if id in id_mappings["workflowId"]["map"]:
        id = id_mappings["workflowId"]["map"]["id"]
    elif id_mappings["workflowId"]["fallback"]:
        id = id_mappings["workflowId"]["fallback"]
    return id

def get_subscriptionId(id):
    # UPDATE_EMAIL_SUBSCRIPTION
    if id in id_mappings["subscriptionId"]["map"]:
        id = id_mappings["subscriptionId"]["map"]["id"]
    elif id_mappings["subscriptionId"]["fallback"]:
        id = id_mappings["subscriptionId"]["fallback"]
    return id

def get_recipientUserIds(id_list):
    # NOTIFICATION_STATION
    if isinstance(id_list, list):
        for id in id_list:
            id = get_userId(id)
    return id_list

def get_recipientTeamIds(id_list):
    # NOTIFICATION_STATION
    if isinstance(id_list, list):
        for id in id_list:
            id = get_teamId(id)
    return id_list

def get_owners(id_list):
    # LEAD_ASSIGNMENT
    if isinstance(id_list, list):
        for id in id_list:
            id = get_ownerId(id)
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
    return attribute_to_getter[attribute](value_origin)
