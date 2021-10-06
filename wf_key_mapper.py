import json
from segment_parser import parse_segments, parse_reEnrollment
import config
import logger
from id_mapper import get_target_id

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
    assert isinstance(value_origin["excludedWorkflows"], list)
    workflows_list_copy = []
    for wf_id in value_origin["excludedWorkflows"]:
        mapped_wf_id = get_target_id("workflowId", wf_id)
        if mapped_wf_id is None:
            logger.log_event("concurrent_workflow_dependency", {"workflowId": str(wf_id), "substituted": False})
        else:
            logger.log_event("concurrent_workflow_dependency", {"workflowId": str(wf_id), "substituted": True})
            workflows_list_copy.append(mapped_wf_id)
    value_origin["excludedWorkflows"] = workflows_list_copy
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
    assert isinstance(value_origin, list)
    list_copy = []
    for list_id in value_origin:
        mapped_list_id = get_target_id("listId", list_id)
        if mapped_list_id is None:
            logger.log_event("suppression_list_dependency", {"listId": str(list_id), "substituted": False})
        else:
            logger.log_event("suppression_list_dependency", {"listId": str(list_id), "substituted": True})
            list_copy.append(mapped_list_id)
    return list_copy

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
    if "staticDateAnchor" in value_origin:
        logger.log_event("placeholder_workflow_date_anchor")
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
