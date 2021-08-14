import json

###
# Configuration
###

name_prefix = "migrated_v3_"
all_enabled = False

###
# Getter functions
###

def get_unenrollmentSetting(value_origin):
    return value_origin

def get_actions(value_origin):
    return value_origin

def get_goalCriteria(value_origin):
    return value_origin

def get_name(value_origin):
    return name_prefix + value_origin

def get_suppressionListIds(value_origin):
    return value_origin

def get_enabled(value_origin):
    if all_enabled:
        return True
    else:
        return value_origin

def get_segmentCriteria(value_origin):
    return value_origin

def get_reEnrollmentTriggerSets(value_origin):
    return value_origin

key_to_getter = {
    "unenrollmentSetting": get_unenrollmentSetting,
    "actions": get_actions,
    "goalCriteria": get_goalCriteria,
    "name": get_name,
    "suppressionListIds": get_suppressionListIds,
    "enabled": get_enabled,
    "segmentCriteria": get_segmentCriteria,
    "reEnrollmentTriggerSets": get_reEnrollmentTriggerSets,
}

###
# External interface
###

def get_wf_key_value(key, value_origin):
    return key_to_getter[key](value_origin)
