# all configuration variables collected here, to be imported in other modules as per https://docs.python.org/3/faq/programming.html#id11

import json
from dotenv import dotenv_values
env_config = dotenv_values(".env")
hapikey_origin = env_config["HAPIKEY_ORIGIN"]
hapikey_target = env_config["HAPIKEY_TARGET"]

# list_copy.py

list_name_prefix = "[mig_real_v2] "

# workflow_copy.py

action_placeholder_property = "message"

# segment_parser.py

# contact string property
placeholder_property = "message"

# deal string property
placeholder_deal_property = "dealname"

# engagement string property
placeholder_engagement_property = "hs_note_body"

# wf_key_mapper.py

name_prefix = "migrated_v15_"
all_enabled = False
staticDateDummy = {"staticDateAnchor": "01/31/2022"}

###
# Read all input files
###

with open("inputs/segment_schemata.json", "r") as read_file:
    segment_schemata = json.load(read_file)
with open("inputs/action_schemata.json", "r") as read_file:
    action_schemata = json.load(read_file)
with open("inputs/wf_schema.json", "r") as read_file:
    wf_schema = json.load(read_file)


with open("inputs/reference_properties.json", "r") as read_file:
    reference_properties = json.load(read_file)
with open("inputs/reference_owner_properties.json", "r") as read_file:
    reference_owner_properties = json.load(read_file)


def string_echo(some_string):
    return some_string

with open("inputs/id_mappings.json", "r") as read_file:
    id_mappings = json.load(read_file, parse_int=string_echo)

#test = id_mappings["emailContentId"]["map"]["10387829496"]
#print(test)
#print(type(test))