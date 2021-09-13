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
        obj_id = id_mappings["workflowId"]["map"][obj_id]
    elif "fallback" in id_mappings["workflowId"]:
        obj_id = id_mappings["workflowId"]["fallback"]
    return obj_id

def get_emailContentId(obj_id):
    # NOTIFICATION, EMAIL
    if obj_id in id_mappings["emailContentId"]["map"]:
        obj_id = id_mappings["emailContentId"]["map"][obj_id]
    elif "fallback" in id_mappings["emailContentId"]:
        obj_id = id_mappings["emailContentId"]["fallback"]
    return obj_id

def get_userId(obj_id):
    # SMS_NOTIFICATION
    ## user ID values appear unchanged
    return obj_id
    #if obj_id in id_mappings["userId"]["map"]:
    #    obj_id = id_mappings["userId"]["map"][obj_id]
    #elif "fallback" in id_mappings["userId"]:
    #    obj_id = id_mappings["userId"]["fallback"]
    #return obj_id

def get_teamId(obj_id):
    # LEAD_ASSIGNMENT
    ## team ID values appear unchanged after all
    return obj_id
    #if obj_id is None:
    #    return obj_id
    #elif obj_id in id_mappings["teamId"]["map"]:
    #    obj_id = id_mappings["teamId"]["map"][obj_id]
    #elif "fallback" in id_mappings["teamId"]:
    #    obj_id = id_mappings["teamId"]["fallback"]
    # is either None or single-valued
    #return obj_id

def get_ownerId(obj_id):
    obj_id=str(obj_id)
    # DEAL, TASK
    if obj_id in id_mappings["ownerId"]["map"]:
        obj_id = id_mappings["ownerId"]["map"][obj_id]
    elif "fallback" in id_mappings["ownerId"]:
        obj_id = id_mappings["ownerId"]["fallback"]
    return obj_id

def get_listId(obj_id):
    # UPDATE_LIST
    if obj_id in id_mappings["listId"]["map"]:
        obj_id = id_mappings["listId"]["map"][obj_id]
    elif "fallback" in id_mappings["listId"]:
        obj_id = id_mappings["listId"]["fallback"]
    return obj_id

def get_subscriptionId(obj_id):
    # UPDATE_EMAIL_SUBSCRIPTION
    if obj_id in id_mappings["subscriptionId"]["map"]:
        obj_id = id_mappings["subscriptionId"]["map"][obj_id]
    elif "fallback" in id_mappings["subscriptionId"]:
        obj_id = id_mappings["subscriptionId"]["fallback"]
    return obj_id

def get_formId(obj_id):
    # used in segment parser
    if obj_id in id_mappings["formId"]["map"]:
        obj_id = id_mappings["formId"]["map"][obj_id]
    elif "fallback" in id_mappings["formId"]:
        obj_id = id_mappings["formId"]["fallback"]
    return obj_id

def get_pageId(obj_id):
    # used in segment parser
    if obj_id in id_mappings["pageId"]["map"]:
        obj_id = id_mappings["pageId"]["map"][obj_id]
    elif "fallback" in id_mappings["pageId"]:
        obj_id = id_mappings["pageId"]["fallback"]
    return obj_id

def get_ctaId(obj_id):
    # used in segment parser
    if obj_id in id_mappings["ctaId"]["map"]:
        obj_id = id_mappings["ctaId"]["map"][obj_id]
    elif "fallback" in id_mappings["ctaId"]:
        obj_id = id_mappings["ctaId"]["fallback"]
    return obj_id

def get_recipientUserIds(id_list):
    # NOTIFICATION_STATION
    #id_list_copy = []
    #if isinstance(id_list, list):
    #    for obj_id in id_list:
    #        id_list_copy.append(get_userId(obj_id))
    #    return id_list_copy
    return id_list

def get_recipientTeamIds(id_list):
    # NOTIFICATION_STATION
    #id_list_copy = []
    #if isinstance(id_list, list):
    #    for obj_id in id_list:
    #        id_list_copy.append(get_teamId(obj_id))
    #    return id_list_copy
    return id_list

def get_owners(id_list):
    # LEAD_ASSIGNMENT
    id_list_copy = []
    if isinstance(id_list, list):
        for obj_id in id_list:
            mapped_owner = get_ownerId(obj_id)
            if mapped_owner is None:
                raise ValueError("Owner " + str(obj_id) + " not mapped.")
            id_list_copy.append(mapped_owner)
        return id_list_copy
    return id_list

# def get_filters(filters):
#     # BRANCH
#     dummy_filter = """
#     [
#         [
#             {
#                 "operator": "IS_NOT_EMPTY",
#                 "filterFamily": "PropertyValue",
#                 "withinTimeMode": "PAST",
#                 "type": "datetime",
#                 "property": "createdate"
#             }
#         ]
#     ]
#     """
#     #return json.loads(dummy_filter)
#     return parse_segments(filters)

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
    #"filters": get_filters,
    "formId": get_formId,
    "pageId": get_pageId,
    "ctaId": get_ctaId,
}

###
# External interface
###

def get_target_id(attribute, value_origin):
    if value_origin is None:
        raise ValueError("value_origin must not be None in function get_target_id")
    elif value_origin == "":
        return ""
    else:
        # will look up the mapping in id_mappings.json
        # if there is no mapping it will apply any fallback value provided
        # if there is no mapping and no fallback, it RETURNS THE ORIGINAL VALUE
        # (remove mappings and fallback if an ID should not be changed)
        return attribute_to_getter[attribute](value_origin)
