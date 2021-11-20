import json
from typing import Any, Tuple
import pandas as pd
import pickle

object_type = ""
object_id = ""
segment_context = ""
workflow_flow_id = ""

#full_log = []
#full_todo = []
#full_dependencies = []

#todo_unique = set()
#dependencies_unique = set()
#todo = []
#dependencies = []

#todo_unique_dict = {
#    "branch": "some instructions"
#}

# a task is a dict that contains a "todo" key (str)

all_tasks = []
object_tasks = {}

list_url_prefix = "https://app.hubspot.com/contacts/2327438/lists/"
workflow_url_prefix = "https://app.hubspot.com/workflows/2327438/flow/"

def push_object_tasks():
    global object_tasks
    if "copy_failure" in object_tasks:
        all_tasks.append(object_tasks["copy_failure"][0])
    else:
        for category in object_tasks:
            for task in object_tasks[category]:
                all_tasks.append(task)
    object_tasks = {}

def create_task(category: str, todo: str, singleton_category: bool = False, count: bool = False, details: dict = {}) -> None:
    global object_id
    global object_type
    global segment_context
    global object_tasks
    assert category != "" and todo != ""
    if object_type == "active_list":
        url = list_url_prefix + str(object_id)
    else:
        url = workflow_url_prefix + str(object_id)
    assert not (singleton_category and count)
    task = {"todo": todo,
            "object_type": object_type,
            "object_id": object_id,
            "segment_context": segment_context,
            "url_original_portal": url}
    task.update(details)
    if singleton_category:
        if category not in object_tasks:
            object_tasks[category] = [task]
    elif count:
        if category not in object_tasks:
            task.update({"count": 1})
            object_tasks[category] = [task]
        else:
            object_tasks[category][0]["count"] += 1
    else:
        if category not in object_tasks:
            object_tasks[category] = []
        object_tasks[category].append(task)




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
        push_object_tasks()
        try:
            assert obj_type in ["static_list", "active_list", "workflow"]
        except:
            print(obj_type)
            assert False
        object_id = str(obj_id)
        object_type = obj_type
        segment_context = ""
        workflow_flow_id = flow_id
        todo_unique = set()
        dependencies_unique = set()
        todo = []
        dependencies = []
        log_event("copy_start")

def set_segment_context(context: str) -> None:
    global segment_context
    assert context in ["enrollment", "reenrollment", "branching", "goal"]
    segment_context = context

def get_logging_object() -> Tuple[str, str]:
    return object_type, object_id

def log_event(event_key: str, event_log: dict = {}) -> None:
    global segment_context
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
        if event_log["substituted"] == False:
            create_task("skipped_suppression_list", "A suppression list (listId " + str(event_log["listId"]) + ") was omitted from the migrated workflow. Add it manually.")
        #ok
        pass
    elif event_key == "concurrent_workflow_dependency":
        #workflow concurrency control
        if event_log["substituted"] == False:
            create_task("concurrent_workflow_unenrollment", "This workflow could not be set to auto-unenroll the contact from another workflow (workflowId " + str(event_log["workflowId"]) + "). Set it manually.")
        #ok
        pass
    elif event_key == "placeholder_action":
        category = "placeholder_action_" + str(event_log["type"])
        create_task(category, "A workflow action (type " + str(event_log["type"]) + ") was migrated as a placeholder. Replace it with the correct action.", False, True)
    elif event_key == "todo_action":
        category = "todo_action_" + str(event_log["type"])
        create_task(category, "A workflow action (type " + str(event_log["type"]) + ") requires manual inspection, and an additional \"to do\" reminder action was placed in front of it. Inspect the workflow action and delete the reminder action.", False, True)
    elif event_key in ["placeholder_segment", "placeholder_deal_subsegment", "placeholder_engagement_subsegment"]:
        category = "placeholder_segment_" + str(segment_context) + "_" + str(event_log["type"])
        create_task(category, "A " + str(segment_context) + "filter condition (type " + str(event_log["type"]) + ") was migrated as a placeholder. Replace it with the correct filter.", False, True)
    elif event_key == "placeholder_ils_filter":
        create_task("placeholder_ils_filter", "This list is in a new format that cannot be parsed yet. A single placeholder filter was created. Re-create its correct filter conditions manually.")
    elif event_key == "placeholder_workflow_date_anchor":
        #ok
        #TODO create task
        pass
    elif event_key == "branching_action":
        create_task("branching_action", "For each if-then branching action, any \"middle\" branches and their dependent actions, and all \"go to other action\" would be missing. Recreate them manually. Branch labels (which are purely cosmetic) have also not been migrated", False, True)
        #create_task("branching_goto_action", "This workflow contains if-then-branching. The original workflow may contain \"go to other action\" actions, which would not have been migrated. Check whether there were any such actions in the original workflow, then manually recreate them.", True, False)
        #create_task("cosmetic", "This workflow contains if-then-branching actions. The branch names/labels have not been migrated. This omission is purely cosmetic. You can re-create the branch names manually.", True, False)
        pass
    elif event_key == "skipped_reenrollment_trigger":
        category = "skipped_reenrollment_trigger_" + str(event_log["type"])
        create_task(category, "A reenrollment condition (type " + str(event_log["type"]) + ") could not be migrated/activated. Add it manually (you may need to re-create the corresponding enrollment condition first)", False, True)
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
        create_task(event_key, "This object could not be migrated. Re-build it manually.", False, True)
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
    #event = {"object_type": object_type,
    #         "object_id": object_id,
    #         "segment_context": segment_context,
    #         "log_key": event_key}
    #event.update(event_log)
    #full_log.append(event.copy())

def write_log(log_file_name: str) -> None:
    log_df = pd.DataFrame(full_log)
    log_df.to_csv(log_file_name+".csv", index=False)
    with open(log_file_name+".pickle", 'wb') as handle:
        pickle.dump(full_log, handle, protocol=pickle.HIGHEST_PROTOCOL)

def write_todo(log_file_name: str) -> None:
    todo_df = pd.DataFrame(all_tasks)
    todo_df = todo_df.sort_values(by=["object_id"])
    todo_df.to_csv(log_file_name+".csv", index=False)
    todo_df.to_excel(log_file_name+".xlsx", index=False)