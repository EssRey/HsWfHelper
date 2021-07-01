from workflow_copy import copy_all_workflows
from dotenv import dotenv_values
config = dotenv_values(".env")
hapikey_origin = config["HAPIKEY_ORIGIN"]
hapikey_target = config["HAPIKEY_TARGET"]


# crawl through every workflow, take the enrolled list, and keep the vids
# assign flowid_id
# collect these values

# invert: collect values for each vid

# create enumeration property with all possible values

# crawl through all contacts, set the enumeration value


copy_all_workflows(hapikey_origin=hapikey_origin, hapikey_target=hapikey_target, silent=True, simulate=True)