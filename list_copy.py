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

#def write_list_id_map(file_name: str = "active_lists"):
#    output_dict = {"listId": {"map": list_id_map, "fallback": None}}
#    with open("id_mappings/" + file_name + ".json", "w") as data_file:
#        json.dump(output_dict, data_file, indent=2)

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
    # double-check types
    for key_origin in origin_list:
        if key_origin in target_list:
            if type(origin_list[key_origin]) != type(target_list[key_origin]):
                #raise TypeError(str(logger.object_type)+"_"+str(logger.object_id) + " " + str(key_origin) + " type discrepancy:")
                print(str(logger.object_type)+"_"+str(logger.object_id) + " " + str(key_origin) + " type discrepancy:")
                print(origin_list)
                print(target_list)
    return target_list

#-------------
# Active list copy related functions (external interface)
#-------------
def copy_list(list_id, hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, simulate=False):
    body = process_list(list_id, hapikey=hapikey_origin)
    if not simulate:
        r = requests.post(url_create_list(hapikey_target), json = body)
        if not r:
            with open("playground/logs/list_v30_"+str(list_id)+"_"+str(r.status_code)+".json", "w") as data_file:
                json.dump(r.json(), data_file, indent=2)
            print("List " + str(list_id) + " could not be re-created. It will not me included in id mappings, and dependencies on it will not be flagged.")
            logger.log_event("asset_creation_failure", {"listId": str(list_id)})
        else:
            #print("List " + str(list_id) + " copied successfully (new ID: " + str(r.json()["listId"]) + ").")
            list_id_map[list_id] = str(r.json()["listId"])

def copy_all_lists(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, simulate=False):
    all_lists = all_lists_raw(hapikey=hapikey_origin)
    for mylist in all_lists:
        if "deleted" in mylist and mylist["deleted"]==True:
            pass
        else:
            copy_list(mylist["listId"], hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, simulate=simulate)

def dump_list(list_id, hapikey=hapikey_origin):
    origin_list = requests.get(url_list(list_id, hapikey)).json()
    return origin_list

def dump_all_lists(hapikey_origin=hapikey_origin, portal_identifier="TEST"):
    all_lists = all_lists_raw(hapikey=hapikey_origin)
    output_lists = []
    for mylist in all_lists:
        if "deleted" in mylist and mylist["deleted"]==True:
            pass
        else:
            proc_list = dump_list(mylist["listId"], hapikey=hapikey_origin)
            output_lists.append(proc_list)
    with open("playground/logs/"+portal_identifier+"_all_lists.txt", "w") as f:
        for wf in output_lists:
            f.write("%s\n" % wf)

if __name__ == "__main__":
    copy_all_lists(simulate=True)
    #dump_all_lists(hapikey_origin="hapikey", portal_identifier="CUSTOMER")
    #logger.write_log("my_log")
    #print(all_lists_raw()[0]["listId"])

