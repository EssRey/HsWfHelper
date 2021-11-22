import json
import config
import logger

###
# Configuration
###

id_mappings = config.id_mappings

###
# Getter functions
###

def get_generic_id(attribute, obj_id):
    if str(obj_id) in id_mappings[attribute]["map"]:
        obj_id = id_mappings[attribute]["map"][str(obj_id)]
    elif "fallback" in id_mappings[attribute]:
        mapped_obj_id = id_mappings[attribute]["fallback"]
        #print("Cannot map " + str(attribute) + " " +  str(obj_id))
        obj_id = mapped_obj_id
    return obj_id

def get_workflowId(obj_id):
    # WORKFLOW_ENROLLMENT
    return get_generic_id("workflowId",obj_id)

def get_emailContentId(obj_id):
    # NOTIFICATION, EMAIL
    return get_generic_id("emailContentId",obj_id)

def get_userId(obj_id):
    # SMS_NOTIFICATION
    ## user ID values appear unchanged
    return obj_id

def get_teamId(obj_id):
    # LEAD_ASSIGNMENT
    ## team ID values appear unchanged after all
    return obj_id

def get_ownerId(obj_id):
    # DEAL, TASK
    mapped_value = get_generic_id("ownerId", obj_id)
    if isinstance(obj_id,int) and mapped_value:
        return int(mapped_value)
    else:
        return mapped_value

def get_listId(obj_id):
    # UPDATE_LIST
    return get_generic_id("listId",obj_id)


def get_subscriptionId(obj_id):
    # UPDATE_EMAIL_SUBSCRIPTION
    return get_generic_id("subscriptionId",obj_id)

def get_formId(obj_id):
    # used in segment parser
    return get_generic_id("formId",obj_id)

def get_pageId(obj_id):
    # used in segment parser
    return get_generic_id("pageId",obj_id)

def get_ctaId(obj_id):
    # used in segment parser
    return get_generic_id("ctaId",obj_id)

def get_recipientUserIds(id_list):
    # NOTIFICATION_STATION
    return id_list

def get_recipientTeamIds(id_list):
    # NOTIFICATION_STATION
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
#     pass

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
        # if there is no mapping it will apply any fallback value provided (which may be null/None)
        # if there is no mapping and no fallback, it RETURNS THE ORIGINAL VALUE
        # (remove mappings and fallback if an ID should not be changed)
        substitution_value = attribute_to_getter[attribute](value_origin)
        logger.log_event("id_substitution", {"type": str(attribute), "original_id": str(value_origin), "mapped_id": str(substitution_value)})
        return substitution_value

def set_id(attribute, new_key, new_value):
    if attribute in id_mappings:
        id_mappings[attribute]["map"][str(new_key)] = new_value

