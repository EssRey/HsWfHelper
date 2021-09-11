import csv
import glob
import json

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
                base_dict[keyword]["map"][row[0]] = row[1]

with open("id_mappings.json", "w") as data_file:
    json.dump(base_dict, data_file, indent=2)