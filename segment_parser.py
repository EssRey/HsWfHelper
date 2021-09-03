import json
from id_mapper import get_target_id
from functools import partial

###
# Configuration
###

# contact string property
placeholder_property="message"
# deal string property
placeholder_deal_property="dealname"
#logger = {"withinTimeMode": []}
with open("segment_schemata.json", "r") as read_file:
    segment_schemata = json.load(read_file)
with open("id_mappings.json", "r") as read_file:
    id_mappings = json.load(read_file)

with open("reference_properties.json", "r") as read_file:
    reference_properties = json.load(read_file)


owner_properties_dict = {
    "deal": [
        "hubspot_owner_id"
    ],
    "contact": [
        "hubspot_owner_id"
    ],
    "lineitem": [
    ]
}


all_segments_ever = {}
def print_s():
    print(all_segments_ever)


###
# Functions
###

def segment_processor(segment, owner_properties=owner_properties_dict):
    # validation of filterFamily type and top-level keys
    schema = {}
    try:
        schema = segment_schemata[segment["filterFamily"]]
        schema.update(segment_schemata["COMMON"])
        assert set(segment.keys()).issubset(set(schema.keys()))
    except KeyError:
        print("Unknown segment filterFamily in following segment: " + json.dumps(segment))
    except AssertionError:
        print("this segment contains unknown keys: " + json.dumps(segment))

    #temp
    #if segment["filterFamily"] not in all_segments_ever:
    #    all_segments_ever[segment["filterFamily"]] = [segment]
    #else:
    #    all_segments_ever[segment["filterFamily"]].append(segment)
    # /temp

    def deal_property_placeholder(segment):
        placeholder_sub_segment = {
            "operator": "EQ",
            "filterFamily": "DealProperty",
            "withinTimeMode": "PAST",
            "propertyObjectType": "DEAL",
            "type": "string",
            "property": placeholder_deal_property,
            "value": json.dumps(segment)
        }
        return placeholder_sub_segment

    operation_handlers = {
        "pass": process_pass,
        "ID_formId": partial(process_get_id, id_type="formId"),
        "ID_pageId": partial(process_get_id, id_type="pageId"),
        "ID_ctaId": partial(process_get_id, id_type="ctaId"),
        "ID_workflowId": partial(process_get_id, id_type="workflowId"),
        "ID_listId": partial(process_get_id, id_type="listId"),
        "DICT_dealsFilter": process_dealsFilter,
        "DICT_engagementsFilter": process_engagementsFilter,
        "DICT_emailEventFilter": process_emailEventFilter,
        "DICT_subscriptionsFilter": process_subscriptionFilter,
        "PROP_contact_property": process_pass,
        "PROP_company_property": process_pass,
        "PROP_deal_or_lineitem_property": process_pass,
        "?(can drop?)": process_pass,
        "?": process_pass
    }

    def process_pass(value):
        return value, []

    def process_get_id(id_type, origin_id):
        mapped_value = get_target_id(id_type, origin_id)
        if mapped_value is None:
            return None, "PLACEHOLDER_ABORT"
        else:
            return mapped_value, []



    def process_emailEventFilter(value_dict):
        return value_dict

    def process_subscriptionFilter(value_dict):
        return value_dict

    def process_engagementsFilter(value_dict):
        return value_dict

    def process_dealsFilter(value_dict):
        return process_subsegment_filters("engagementsFilter", value_dict)

    def process_subsegment_filters(key, value_dict):
        assert isinstance(value_dict, dict)
        assert len(value_dict)==1
        processed_filterLines = []

        event_log_dealsFilter = []

        for sub_segment in value_dict["filterLines"]:
            assert len(sub_segment) == 2
            assert isinstance(sub_segment["filter"], dict)
            processed_sub_segment = sub_segment.copy()
            for sub_key in sub_segment["filter"]:
                assert schema[sub_key] != "DO_NOT_PROCESS"
            processed_sub_segment["filter"], event_log_filter = segment_processor(sub_segment["filter"])
            processed_filterLines.append(processed_sub_segment)
            if len(event_log_filter) > 0:
                event_log_dealsFilter.append(event_log_filter)
        return {"filterLines": processed_filterLines}, event_log_dealsFilter

    # this function uses the entire segment (not just its parameters)
    def owner_id_check(value, prop, object_type):
        if (object_type == "DEAL" and prop in owner_properties_dict["deal"] or
                object_type == "LINE_ITEM" and prop in owner_properties_dict["lineitem"] or
                object_type == "COMPANY" and prop in owner_properties_dict["company"] or
                object_type == "CONTACT" and prop in owner_properties_dict["contact"]):
            substitution_result = get_target_id("ownerId", value)
            if substitution_result is None:
                return {"log_type":"SUBSTITUTION_ERROR", "log":"cannot_map_ownerId "+str(value)}
            else:
                value = substitution_result
        return value

    processed_segment = {}
    event_log_segment = []
    for key in segment:
        assert isinstance(key, str)
        if schema[key] == "DO_NOT_PROCESS":
            return segment_placeholder(segment), [{"log_type":"placeholder_segment_"+segment["filterFamily"], "log":json.dumps(segment)}]
        operation_handler = operation_handlers[schema[key]]
        processed_segment[key], event_log_key = operation_handler(segment[key])
        if event_log_key == "PLACEHOLDER_ABORT":
            event_log_segment.append({"log_type":"abort_substitution_" + key + "_in_" + segment["filterFamily"], "log":json.dumps(segment)})
            return segment_placeholder(segment), event_log_segment
        if len(event_log_key) > 0:
            event_log_segment.append({"log_type": "key_"+key, "log":event_log_key})

    # substitute owner ID if owner property
    if "value" in processed_segment:
        object_type = None
        placeholder = segment_placeholder(segment)
        if processed_segment["filterFamily"]=="DealProperty":
            assert "propertyObjectType" in processed_segment
            object_type = processed_segment["propertyObjectType"]
            placeholder = deal_property_placeholder(segment)
        elif processed_segment["filterFamily"]=="CompanyPropertyValue":
            object_type = "COMPANY"
        elif processed_segment["filterFamily"]=="PropertyValue":
            object_type = "CONTACT"
        if object_type:
            confirmed_value = owner_id_check(processed_segment["value"],
                                            processed_segment["property"],
                                            object_type)
            if isinstance(confirmed_value, dict):
                assert confirmed_value["type"]=="SUBSTITUTION_ERROR"
                event_log_segment.insert(0, {"log_type":"placeholder_segment_OWNERID_"+processed_segment["filterFamily"],
                                            "log":confirmed_value["log"] + " (" + json.dumps(segment) + ")"})
                return placeholder, event_log_segment
            else:
                processed_segment["value"] = confirmed_value
    return processed_segment, event_log_segment


###
# External interface
###

def segment_placeholder(segment):
    placeholder = {"filterFamily": "PropertyValue",
            "operator": "EQ",
            "withinTimeMode": "PAST",
            "property": placeholder_property,
            "value": json.dumps(segment),
            "type": "string"
            }
    return placeholder

def parse_segments(segments, owner_properties=["hubspot_owner_id"], processor=segment_processor):
    assert isinstance(segments, list)
    processed_segments = []
    for sufficient_group in segments:
        assert isinstance(sufficient_group, list)
        processed_sufficient_group = []
        for necessary_condition in sufficient_group:
            assert isinstance(necessary_condition, dict)
            processed_necessary_condition = processor(necessary_condition, owner_properties)
            processed_sufficient_group.append(processed_necessary_condition)
        processed_segments.append(processed_sufficient_group)
    return processed_segments

def parse_reEnrollment(triggers, owner_properties=["hubspot_owner_id"]):
    if not isinstance(triggers, list):
        print("cannot parse reEnrollmentTriggerSets, returning empty segments")
        return []
    processed_triggers = []
    # process here
    return processed_triggers

