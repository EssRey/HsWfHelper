import json

###
# Missing: read the actual mappings from configuration file
###

###
# Stub getter functions
###

def get_workflowId(id):
    # WORKFLOW_ENROLLMENT
    return id

def get_emailContentId(id):
    #NOTIFICATION, EMAIL
    return id

def get_userId(id):
    # SMS_NOTIFICATION
    return id

def get_teamId(id):
    # SMS_NOTIFICATION
    return id

def get_ownerId(id):
    # DEAL, TASK
    return id

def get_listId(id):
    # UPDATE_LIST
    return id

def get_subscriptionId(id):
    # UPDATE_EMAIL_SUBSCRIPTION
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

def get_target_id(attribute, value_origin):
    return attribute_to_getter[attribute](value_origin)
