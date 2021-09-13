import json
from id_mapper import get_target_id
from functools import partial

###
# Configuration
###

# contact string property
placeholder_property = "message"

# deal string property
placeholder_deal_property = "dealname"

# engagement string property
placeholder_engagement_property = "hs_note_body"

with open("segment_schemata.json", "r") as read_file:
    segment_schemata = json.load(read_file)

with open("reference_owner_properties.json", "r") as read_file:
    owner_properties_dict = json.load(read_file)

###
# Functions
###

def owner_id_check(value, prop, object_type):
    if (object_type == "DEAL" and prop in owner_properties_dict["deal"] or
            object_type == "LINE_ITEM" and prop in owner_properties_dict["line_item"] or
            object_type == "COMPANY" and prop in owner_properties_dict["company"] or
            object_type == "CONTACT" and prop in owner_properties_dict["contact"] or
            object_type == "ENGAGEMENT" and prop in owner_properties_dict["engagement"]):
        substitution_result = get_target_id("ownerId", value)
        if substitution_result is None:
            return {"log_type":"SUBSTITUTION_ERROR", "log":"cannot_map_ownerId "+str(value)}
        else:
            value = substitution_result
    return value

def segment_processor(segment):
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

    def engagement_property_placeholder(segment):
        placeholder_sub_segment = {
            "operator": "EQ",
            "filterFamily": "Engagement",
            "propertyObjectType": "ENGAGEMENT",
            "type": "string",
            "property": placeholder_engagement_property,
            "strValue": json.dumps(segment)
        }
        return placeholder_sub_segment

    def process_pass(value):
        return value, []

    def process_get_id(origin_id, id_type):
        mapped_value = get_target_id(id_type, origin_id)
        if mapped_value is None:
            return None, "PLACEHOLDER_ABORT"
        else:
            return mapped_value, []

    def process_emailEventFilter(value_dict):
        # not implemented while emailCampaignID migration issue not clarified
        # once it is, will have to call https://legacydocs.hubspot.com/docs/methods/cms_email/get-the-details-for-a-marketing-email
        # and then look at allEmailCampaignIds or primary campaign id or campaign id group (not sure which one when)
        return None, "PLACEHOLDER_ABORT"

    def process_subscriptionsFilter(value_dict):
        assert isinstance(value_dict, dict)
        assert len(value_dict)==2
        processed_dict = value_dict.copy()
        subscription_array = []
        for subscription in value_dict["subscriptionIds"]:
            mapped_subscription = get_target_id("subscriptionId", subscription)
            if mapped_subscription is None:
                return None, "PLACEHOLDER_ABORT"
            else:
                subscription_array.append(mapped_subscription)
        processed_dict["subscriptionIds"] = subscription_array
        return processed_dict, []

    def process_engagementsFilter(value_dict):
        assert isinstance(value_dict, dict)
        assert len(value_dict)==1
        processed_filters = []
        event_log_engagementsFilter = []
        for sub_segment in value_dict["filters"]:
            assert isinstance(sub_segment, dict)
            #processed_sub_segment = sub_segment.copy()
            for sub_key in sub_segment:
                assert schema[sub_key] != "DO_NOT_PROCESS"
            processed_sub_segment, event_log_filter = segment_processor(sub_segment)
            processed_filters.append(processed_sub_segment)
            if len(event_log_filter) > 0:
                event_log_engagementsFilter.append(event_log_filter)
        return {"filters": processed_filters}, event_log_engagementsFilter

    def process_dealsFilter(value_dict):
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
        "DICT_subscriptionsFilter": process_subscriptionsFilter,
        "PROP_contact_property": process_pass,
        "PROP_company_property": process_pass,
        "PROP_deal_or_lineitem_property": process_pass,
        "PROP_engagement_property": process_pass
    }

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
    if "value" in processed_segment or "strValue" in processed_segment:
        object_type = None
        placeholder = segment_placeholder(segment)
        if processed_segment["filterFamily"]=="DealProperty":
            #assert "propertyObjectType" in processed_segment
            object_type = processed_segment["propertyObjectType"]
            placeholder = deal_property_placeholder(segment)
        elif processed_segment["filterFamily"]=="Engagement":
            #assert "propertyObjectType" in processed_segment
            object_type = processed_segment["propertyObjectType"]
            placeholder = engagement_property_placeholder(segment)
        elif processed_segment["filterFamily"]=="CompanyPropertyValue":
            object_type = "COMPANY"
        elif processed_segment["filterFamily"]=="PropertyValue":
            object_type = "CONTACT"
        if object_type:
            if "value" in processed_segment:
                owner_array = str(processed_segment["value"]).split(";")
            else:
                owner_array = str(processed_segment["strValue"]).split(";")
            processed_owner_array = []
            for owner in owner_array:


                confirmed_value = owner_id_check(owner,
                                                processed_segment["property"],
                                                object_type)
                if isinstance(confirmed_value, dict):
                    assert confirmed_value["log_type"]=="SUBSTITUTION_ERROR"
                    event_log_segment.insert(0, {"log_type":"placeholder_segment_OWNERID_"+processed_segment["filterFamily"],
                                                "log":confirmed_value["log"] + " (" + json.dumps(segment) + ")"})
                    return placeholder, event_log_segment
                else:
                    processed_owner_array.append(confirmed_value)
            if "value" in processed_segment:
                processed_segment["value"] = ";".join(processed_owner_array)
            else:
                processed_segment["strValue"] = ";".join(processed_owner_array)
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

def parse_segments(segments, processor=segment_processor):
    assert isinstance(segments, list)
    segment_log = []
    processed_segments = []
    for sufficient_group in segments:
        assert isinstance(sufficient_group, list)
        processed_sufficient_group = []
        for necessary_condition in sufficient_group:
            assert isinstance(necessary_condition, dict)
            processed_necessary_condition, necessary_condition_log = processor(necessary_condition)
            processed_sufficient_group.append(processed_necessary_condition)
            if necessary_condition_log != []:
                segment_log.append(necessary_condition_log)
        processed_segments.append(processed_sufficient_group)
    if segment_log != []:
        print(segment_log)
    return processed_segments

def parse_reEnrollment(triggers):
    if not isinstance(triggers, list):
        print("cannot parse reEnrollmentTriggerSets, returning empty segments")
        return []
    processed_triggers = []
    # process here
    return processed_triggers



###
# Temp testing
###

test_engagement = {
    "filterFamily": "Engagement",
    "withinTimeMode": "PAST",
    "engagementsFilter": {
        "filters": [
            {
                "property": "hubspot_owner_id",
                "operator": "SET_ANY",
                "type": "enumeration",
                "strValue": "30612412;39019619",
                "propertyObjectType": "ENGAGEMENT",
                "filterFamily": "Engagement"
            },
            {
                "property": "hubspot_owner_id",
                "operator": "IS_EMPTY",
                "type": "enumeration",
                "propertyObjectType": "ENGAGEMENT",
                "filterFamily": "Engagement"
            },
            {
                "property": "hs_created_by",
                "operator": "SET_ALL",
                "type": "enumeration",
                "strValue": "4678986",
                "propertyObjectType": "ENGAGEMENT",
                "filterFamily": "Engagement"
            },
            {
                "property": "hs_task_completion_date",
                "operator": "IS_NOT_EMPTY",
                "type": "datetime",
                "longValue": 1631387869856,
                "propertyObjectType": "ENGAGEMENT",
                "filterFamily": "Engagement"
            }
        ]
    },
    "propertyObjectType": "ENGAGEMENT"
}

#print(segment_processor(test_engagement))

test_filters = [
    [
        {
            "withinTimeMode": "PAST",
            "page": "",
            "form": "4886fea6-88bf-4025-b338-c65341e5b858",
            "operator": "HAS_NOT_FILLED_OUT_FORM",
            "filterFamily": "FormSubmission"
        },
        {
            "withinTimeMode": "PAST",
            "page": "",
            "form": "a9bb5cc0-81a8-4fc9-8d50-991b5024b260",
            "operator": "HAS_FILLED_OUT_FORM",
            "filterFamily": "FormSubmission"
        }
    ],
    [
        {
            "withinTimeMode": "PAST",
            "operator": "EQ",
            "filterFamily": "PropertyValue",
            "type": "string",
            "property": "test_string_two",
            "value": "ANGEMELDET"
        },
        {
            "withinTimeMode": "PAST",
            "page": "",
            "form": "4886fea6-88bf-4025-b338-c65341e5b858",
            "operator": "HAS_NOT_FILLED_OUT_FORM",
            "filterFamily": "FormSubmission"
        }
    ]
]

test_filters_two = [
    [
        {
            "withinTimeMode": "PAST",
            "page": "",
            "form": "4886fea6-88bf-4025-b338-c65341e5b858",
            "operator": "HAS_NOT_FILLED_OUT_FORM",
            "filterFamily": "FormSubmission"
        }
    ]
]

#parse_segments(test_filters_two)