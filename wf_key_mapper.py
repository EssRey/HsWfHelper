import json
from segment_parser import parse_segments, parse_reEnrollment
import config
import logger

###
# Configuration
###

name_prefix = config.name_prefix
all_enabled = config.all_enabled
staticDateDummy = config.staticDateDummy

###
# Getter functions
###

def get_unenrollmentSetting(value_origin):
    return value_origin

def get_actions(value_origin):
    # currently never called (actions are parsed separately in workflow_copy.py 2021/8/15)
    assert False
    return value_origin

def get_goalCriteria(value_origin):
    logger.set_segment_context("goal")
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
    logger.set_segment_context("enrollment")
    return parse_segments(value_origin)

def get_reEnrollmentTriggerSets(value_origin):
    logger.set_segment_context("reenrollment")
    return parse_reEnrollment(value_origin)

def get_eventAnchor(value_origin):
    print("Changed date of date-centered workflow from "+str(value_origin)+" to a placeholder date("+str(staticDateDummy)+")")
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
