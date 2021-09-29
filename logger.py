object_type = ""
object_id = ""

full_log = []


#-------------
# External logging interface
#-------------

def set_logging_object(obj_type: str, obj_id: Any) -> None:
    assert obj_type in ["static_list", "active_list", "workflow"]
    object_id = str(obj_id)
    object_type = obj_type

def get_logging_object() -> Tuple[str, str]:
    return object_type, object_id

def log_event(event_key: str, event_log: Any) -> None:
    full_log.append({object_type: object_type,
                    object_id: object_id,
                    log_type: "event",
                    log_key: event_key,
                    log: event_log})
