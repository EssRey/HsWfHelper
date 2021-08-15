import json
from segment_parser import parse_segments

###
# Configuration
###

name_prefix = "migrated_v7_"
all_enabled = False
staticDateDummy = {"staticDateAnchor": "01/31/2022"}

###
# Getter functions
###

def get_unenrollmentSetting(value_origin):
    return value_origin

def get_actions(value_origin):
    # currently never called (actions are parsed separately in workflow_copy.py 2021/8/15)
    return value_origin

def get_goalCriteria(value_origin):
    # regular filter parser
    return parse_segments(value_origin)

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
    # regular filter parse
    return parse_segments(value_origin)

def get_reEnrollmentTriggerSets(value_origin):
    # special filter parse
    return value_origin

def get_eventAnchor(value_origin):
    print(value_origin)
    if "staticDateAnchor" in value_origin:
        return staticDateDummy
    else:
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
    "eventAnchor": get_eventAnchor
}

###
# External interface
###

def get_wf_key_value(key, value_origin):
    return key_to_getter[key](value_origin)
