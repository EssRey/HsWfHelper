import csv
import glob
import json
from list_copy import all_lists_raw
import json

# store active list IDs

active_list_ids = [active_list["listId"] for active_list in all_lists_raw()]
with open('inputs/active_list_ids.json', 'w') as file:
    json.dump(active_list_ids, file)

# ID mappings

base_dict = {
    "workflowId": {
        "map": {
        },
        "fallback": None
    },
    "emailContentId": {
        "map": {
        },
        "fallback": None
    },
    "ownerId": {
        "map": {
        },
        "fallback": None
    },
    "listId": {
        "map": {
        },
        "fallback": None
    },
    "subscriptionId": {
        "map": {
        },
        "fallback": None
    },
    "formId": {
        "map": {
        },
        "fallback": None
    },
    "pageId": {
        "map": {
        },
        "fallback": None
    },
    "ctaId": {
        "map": {
        },
        "fallback": None
    }
}

keyword_dict = {
    "OWNER": "ownerId",
    "MARKETING_EMAIL": "emailContentId",
    "LANDING_PAGE": "pageId",
    "FORM": "formId",
    "CTA": "ctaId",
    "BLOG_POST": "pageId",
    "SUBSCRIPTION_DEFINITION": "subscriptionId"
}

def get_key(keyword):
    if keyword in keyword_dict:
        return keyword_dict[keyword]
    else:
        assert keyword in base_dict
        return keyword

files = glob.glob("id_mappings/*.csv")
for filename in files:
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        row_counter = 0
        for row in reader:
            row_counter += 1
            if row_counter == 1:
                assert len(row) == 1
                keyword = get_key(row[0])
            elif row_counter == 2:
                pass
            else:
                assert len(row) == 2
                final_value = row[1]
                base_dict[keyword]["map"][row[0]] = final_value

try:
    with open("id_mappings/staticListIdMapping.json", "r") as read_file:
        base_dict["listId"]["map"].update(json.load(read_file))
except FileNotFoundError:
    print("No static list ID mappings found.")

try:
    with open("id_mappings/dynamicListIdMapping.json", "r") as read_file:
        base_dict["listId"]["map"].update(json.load(read_file))
except FileNotFoundError:
    print("No dynamic list ID mappings found.")

print('please check CTA and subscription ID types')
for id_type in base_dict:
    if id_type not in ["formId", "ownerId"]:#maybe also CTAs?
        for item in base_dict[id_type]["map"]:
            base_dict[id_type]["map"][item] = int(base_dict[id_type]["map"][item])

with open("inputs/id_mappings.json", "w") as data_file:
    json.dump(base_dict, data_file, indent=2)