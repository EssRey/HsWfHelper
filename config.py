# all configuration variables collected here, to be imported in other modules as per https://docs.python.org/3/faq/programming.html#id11

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

name_prefix = "migrated_v11_"
all_enabled = False
staticDateDummy = {"staticDateAnchor": "01/31/2022"}
