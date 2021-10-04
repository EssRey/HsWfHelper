import json
from typing import Any, Tuple

object_type = ""
object_id = ""
segment_context = ""

full_log = []


#-------------
# External logging interface
#-------------

###
# a logged event has the form [TAG, LOG], where TAG is a string and LOG is a dict
###

def set_logging_object(obj_type: str, obj_id: Any) -> None:
    assert obj_type in ["static_list", "active_list", "workflow"]
    object_id = str(obj_id)
    object_type = obj_type
    segment_context = ""

def set_segment_context(context: str) -> None:
    assert context in ["enrollment", "reenrollment", "branching", "goal"]
    segment_context = context

def get_logging_object() -> Tuple[str, str]:
    return object_type, object_id

def log_event(event_key: str, event_log: dict) -> None:
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
        pass
    elif event_key == "top_level_dependency":
        #suppression list etc
        pass
    elif event_key == "placeholder_action":
        pass
    elif event_key == "placeholder_segment":
        pass
    elif event_key == "placeholder_deal_subsegment":
        pass
    elif event_key == "placeholder_engagement_subsegment":
        pass
    elif event_key == "branching_action":
        pass
    elif event_key == "skipped_reenrollment_trigger":
        pass
    else:
        raise ValueError("Unknown logging event key.")
    #stub
    full_log.append({"object_type": object_type,
                    "object_id": object_id,
                    "segment_context": segment_context,
                    "log_type": "event",
                    "log_key": event_key,
                    "log": event_log})
