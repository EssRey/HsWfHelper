#-------------
# Imports
#-------------
import requests, json
#from dotenv import dotenv_values
import time
from segment_parser import parse_segments, segment_placeholder
import config
import logger

#-------------
# Configuration
#-------------

#config = dotenv_values(".env")
hapikey_origin = config.hapikey_origin #config["HAPIKEY_ORIGIN"]
hapikey_target = config.hapikey_target #config["HAPIKEY_TARGET"]
list_name_prefix = config.list_name_prefix
ils_dummy_prefix = config.ils_dummy_prefix
list_id_map = {}

#-------------
# URL getters
#-------------
def url_list(listId, hapikey):
    return "https://api.hubapi.com/contacts/v1/lists/" + str(listId) + "?hapikey=" + hapikey
def url_lists_all(hapikey):
    return "https://api.hubapi.com/contacts/v1/lists/dynamic?hapikey=" + hapikey
def url_create_list(hapikey):
    return "https://api.hubapi.com/contacts/v1/lists?hapikey=" + hapikey


#-------------
# Utility functions
#-------------
def all_lists_raw(hapikey=hapikey_origin):
    base_url = url_lists_all(hapikey) #+"&count=10"
    has_more = True
    additional_parameters = ""
    all_lists = []
    while has_more == True:
        lists = requests.get(base_url + additional_parameters).json()
        all_lists.extend(lists["lists"])
        has_more = lists["has-more"]
        additional_parameters = "&offset=" + str(lists["offset"])
    return all_lists

def create_placeholder_filter(content):
    return [[segment_placeholder(content)]]

def write_list_id_map(file_name: str = "active_lists"):
    output_dict = {"listId": {"map": list_id_map, "fallback": None}}
    with open("id_mappings/" + file_name + ".json", "w") as data_file:
        json.dump(output_dict, data_file, indent=2)

def process_list(list_id, hapikey=hapikey_origin):
    logger.set_logging_object("active_list", list_id)
    origin_list = requests.get(url_list(list_id, hapikey)).json()
    target_list = {}
    target_list["name"] = list_name_prefix + origin_list["name"]
    target_list["dynamic"] = origin_list["dynamic"]
    target_list["archived"] = origin_list["archived"]
    target_list["teamIds"] = []#origin_list["teamIds"]
    target_list["filters"] = parse_segments(origin_list["filters"])
    if "ilsFilterBranch" in origin_list:
        logger.log_event("placeholder_ils_filter")
        target_list["filters"] = create_placeholder_filter(origin_list["ilsFilterBranch"])
        target_list["name"] = ils_dummy_prefix + target_list["name"]
    return target_list

#-------------
# Active list copy related functions (external interface)
#-------------
def copy_list(list_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target):
    body = process_list(list_id, hapikey=hapikey_origin)
    r = requests.post(url_create_list(hapikey_target), json = body)
    if not r:
        with open("playground/logs/list_v30_"+str(list_id)+"_"+str(r.status_code)+".json", "w") as data_file:
            json.dump(r.json(), data_file, indent=2)
        print("List " + str(list_id) + " could not be re-created. It will not me included in id mappings, and dependencies on it will not be flagged.")
        logger.log_event("asset_creation_failure", {"listId": str(list_id)})
    else:
        #print("List " + str(list_id) + " copied successfully (new ID: " + str(r.json()["listId"]) + ").")
        list_id_map[list_id] = str(r.json()["listId"])

def copy_all_lists(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target):
    all_lists = all_lists_raw(hapikey=hapikey_origin)
    for mylist in all_lists:
        if "deleted" in mylist and mylist["deleted"]==True:
            pass
        else:
            copy_list(mylist["listId"], hapikey_origin=hapikey_origin, hapikey_target=hapikey_target)

if __name__ == "__main__":
    #copy_all_lists()
    #write_list_id_map("test_write_v30")
    #for list_id in [524, 641, 894, 988, 992, 8053, 8057, 8063, 8065, 8066, 8070]:
    #    copy_list(list_id)
    copy_list(725)

