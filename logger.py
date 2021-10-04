import json

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
    #stub
    full_log.append({"object_type": object_type,
                    "object_id": object_id,
                    "segment_context": segment_context,
                    "log_type": "event",
                    "log_key": event_key,
                    "log": event_log})
