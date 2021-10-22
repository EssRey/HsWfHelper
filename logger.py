import json
from typing import Any, Tuple
import pandas as pd
import pickle

object_type = ""
object_id = ""
segment_context = ""
workflow_flow_id = ""

full_log = []


#-------------
# External logging interface
#-------------

###
# a logged event has the form [TAG, LOG], where TAG is a string and LOG is a dict
###

def set_logging_object(obj_type: str, obj_id: Any, flow_id: Any = "") -> None:
    global object_id
    global object_type
    global segment_context
    global workflow_flow_id
    if str(obj_id) == object_id and obj_type == object_type:
        return None
    else:
        assert obj_type in ["static_list", "active_list", "workflow"]
        object_id = str(obj_id)
        object_type = obj_type
        segment_context = ""
        workflow_flow_id = flow_id
        log_event("copy_start")

def set_segment_context(context: str) -> None:
    global segment_context
    assert context in ["enrollment", "reenrollment", "branching", "goal"]
    segment_context = context

def get_logging_object() -> Tuple[str, str]:
    return object_type, object_id

def log_event(event_key: str, event_log: dict = {}) -> None:
    if event_key == "segment_dependency":
        #active_list_membership
        #workflow_status
        #has_ever_been_property
        #form_submission
        #marketing_email_activity
        #import
        #behavioral_event_legacy
        #call-to-action
        #ads_interactions
        pass
    elif event_key == "action_dependency":
        #workflow action
        #ok
        pass
    elif event_key == "suppression_list_dependency":
        #suppression list
        #TODO create task for non-substituted id
        #ok
        pass
    elif event_key == "concurrent_workflow_dependency":
        #suppression list
        #TODO create task for non-substituted id
        #ok
        pass
    elif event_key == "placeholder_action":
        #ok
        pass
    elif event_key == "todo_action":
        #ok
        pass
    elif event_key == "placeholder_segment":
        #"type" key holds filterFamily, i.e. segment type
        #ok
        pass
    elif event_key == "placeholder_deal_subsegment":
        #"type" key holds filterFamily, i.e. segment type
        # ok
        pass
    elif event_key == "placeholder_engagement_subsegment":
        #"type" key holds filterFamily, i.e. segment type
        # ok
        pass
    elif event_key == "placeholder_ils_filter":
        #ok
        pass
    elif event_key == "placeholder_workflow_date_anchor":
        #ok
        #TODO create task
        pass
    elif event_key == "branching_action":
        #ok
        pass
    elif event_key == "skipped_reenrollment_trigger":
        #keys are "type" and "detail"
        #ok
        pass
    elif event_key == "asset_creation_failure":
        #keys either "listId" or "workflowId"
        # REDUNDANT (see copy_failure)
        #ok
        pass
    elif event_key == "copy_start":
        #ok
        pass
    elif event_key == "copy_failure":
        #ok
        pass
    elif event_key == "copy_success":
        #ok
        pass
    elif event_key == "see_an_action":
        #any non-branch action
        # has type key
        #ok
        pass
    elif event_key == "see_a_segment":
        #any segment or subsegment
        # has type key
        pass
    elif event_key == "see_a_reenrollment_trigger":
        #any reenrollment trigger
        # has type key
        pass
    else:
        raise ValueError("Unknown logging event key: " + str(event_key))
    event = {"object_type": object_type,
             "object_id": object_id,
             "segment_context": segment_context,
             "log_key": event_key}
    event.update(event_log)
    full_log.append(event.copy())

def write_log(log_file_name: str) -> None:
    log_df = pd.DataFrame(full_log)
    log_df.to_csv(log_file_name+".csv", index=False)
    with open(log_file_name+".pickle", 'wb') as handle:
        pickle.dump(full_log, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #with open('full_log.pickle', 'rb') as handle:
    #    b = pickle.load(handle)