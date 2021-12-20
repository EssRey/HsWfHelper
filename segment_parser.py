import json
from id_mapper import get_target_id
from functools import partial
import config
import logger

###
# Configuration
###

active_list_ids = config.active_list_ids

# contact string property
placeholder_property = config.placeholder_property

# deal string property
placeholder_deal_property = config.placeholder_deal_property

# engagement string property
placeholder_engagement_property = config.placeholder_engagement_property

segment_schemata = config.segment_schemata
reference_owner_properties = config.reference_owner_properties

###
# Functions
###


def owner_id_check(value, prop, object_type):
    if (object_type == "DEAL" and prop in reference_owner_properties["deal"] or
        object_type == "LINE_ITEM" and prop in reference_owner_properties["line_item"] or
        object_type == "COMPANY" and prop in reference_owner_properties["company"] or
        object_type == "CONTACT" and prop in reference_owner_properties["contact"] or
        object_type == "ENGAGEMENT" and prop in reference_owner_properties["engagement"]):
        substitution_result = get_target_id("ownerId", value)
        if substitution_result is None:
            return {"log_type": "SUBSTITUTION_ERROR", "log": "cannot_map_ownerId "+str(value)}
        else:
            value = substitution_result
    return value

def segment_processor(segment):
    logger.log_event("see_a_segment", {"type": segment["filterFamily"]})
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

    # log dependencies that may be missing data
    filter_family = segment["filterFamily"]
    if filter_family == "ListMembership":
        if segment["list"] in active_list_ids:
            logger.log_event("segment_dependency", {"type": filter_family, "listId": str(segment["list"])})
    elif filter_family == "Workflow":
        logger.log_event("segment_dependency", {"type": "workflow", filter_family: str(segment["workflowId"])})
    elif filter_family == "FormSubmission":
        try:
            logger.log_event("segment_dependency", {"type": filter_family, "formId": str(segment["form"])})
        except KeyError:
            logger.log_event("segment_dependency", {"type": filter_family})
    elif filter_family == "Email":
        logger.log_event("segment_dependency", {"type": filter_family, "campaign_emailId": str(segment["emailEventFilter"]["emailId"])})
    elif filter_family == "CTA":
        logger.log_event("segment_dependency", {"type": filter_family, "ctaId": str(segment["value"])})
    elif filter_family in ["Ads", "IntegrationsTimeline", "Event", "Import"]:
        logger.log_event("segment_dependency", {"type": filter_family})
    elif filter_family in ["PropertyValue", "CompanyPropertyValue", "DealProperty"]:
        try:
            if segment["checkPastVersions"] == True:
                if filter_family == "DealProperty":
                    filter_family = filter_family + "_" + str(segment["propertyObjectType"])
                if segment["operator"] == "EQ":
                    logger.log_event("segment_dependency", {"type": filter_family, "property": segment["property"], "detail": "HAS EVER BEEN EQUAL TO filter references property history, which has not been fully migrated"})
                elif segment["operator"] == "NEQ":
                    logger.log_event("segment_dependency", {"type": filter_family, "property": segment["property"], "detail": "HAS NEVER BEEN EQUAL TO filter references property history, which has not been fully migrated"})
                elif segment["operator"] == "CONTAINS":
                    logger.log_event("segment_dependency", {"type": filter_family, "property": segment["property"], "detail": "HAS EVER CONTAINED filter references property history, which has not been fully migrated"})
        except KeyError:
            pass

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
            logger.log_event("placeholder_segment", {"type": segment["filterFamily"]})
            return segment_placeholder(segment), event_log_segment
        if len(event_log_key) > 0:
            event_log_segment.append({"log_type": "key_"+key, "log":event_log_key})

    # substitute owner ID if owner property
    if "value" in processed_segment:
        if isinstance(processed_segment["value"], bool):
            return processed_segment, event_log_segment
    if "strValue" in processed_segment:
        if isinstance(processed_segment["strValue"], bool):
            return processed_segment, event_log_segment
    if "value" in processed_segment or "strValue" in processed_segment:
        object_type = None
        log_event_type = "placeholder_segment"
        placeholder = segment_placeholder(segment)
        if processed_segment["filterFamily"]=="DealProperty":
            #assert "propertyObjectType" in processed_segment
            object_type = processed_segment["propertyObjectType"]
            log_event_type = "placeholder_deal_subsegment"
            placeholder = deal_property_placeholder(segment)
        elif processed_segment["filterFamily"]=="Engagement":
            #assert "propertyObjectType" in processed_segment
            object_type = processed_segment["propertyObjectType"]
            log_event_type = "placeholder_engagement_subsegment"
            placeholder = engagement_property_placeholder(segment)
        elif processed_segment["filterFamily"]=="CompanyPropertyValue":
            object_type = "COMPANY"
        elif processed_segment["filterFamily"]=="PropertyValue":
            object_type = "CONTACT"
        if object_type:
            if "value" in processed_segment:
                #print(processed_segment["value"])
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
                    logger.log_event(log_event_type, {"type": processed_segment["filterFamily"]})
                    return placeholder, event_log_segment
                else:
                    processed_owner_array.append(confirmed_value)
            joined_owner_string = ";".join(processed_owner_array)
            if "value" in processed_segment:
                if str(processed_segment["value"]) != joined_owner_string:
                    processed_segment["value"] = joined_owner_string
            elif "strValue" in processed_segment:
                if str(processed_segment["strValue"]) != joined_owner_string:
                    processed_segment["strValue"] = joined_owner_string
    return processed_segment, event_log_segment


## This is rough way of flagging the usage of any of the opt out properties (which change names across migrated portals, but have no mapping yet).
## Careful with the clumsy recursion here.

def flag_opt_out_property(segment):
    if isinstance(segment, dict):
        for key in segment:
            if isinstance(key, str):
                if "hs_email_optout_" in key:
                    return True
            if isinstance(segment[key], str):
                 if "hs_email_optout_" in segment[key]:
                    return True
            elif isinstance(segment[key], dict) or isinstance(segment[key], list):
                if flag_opt_out_property(segment[key]):
                    return True
    elif isinstance(segment, list):
        for sub_segment in segment:
            if flag_opt_out_property(sub_segment):
                return True
    return False



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
    if flag_opt_out_property(segments):
        logger.log_event("see_opt_out_property", {"type": "segment"})
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
        #the following command would output the legacy event log trail (mostly id substitution errors in 3967897)
        #print(segment_log)
        pass
    return processed_segments

def parse_reEnrollment(triggers):
    if not isinstance(triggers, list):
        print("cannot parse reEnrollmentTriggerSets, returning empty segments")
        return []
    if flag_opt_out_property(segment):
        logger.log_event("see_opt_out_property", {"type": "reEnrollmentTrigger"})
    processed_triggers = []
    for trigger in triggers:
        logger.log_event("see_a_reenrollment_trigger", {"type": trigger[0]["type"]})
        processed_trigger = []
        assert isinstance(trigger, list)
        if len(trigger) == 2:
            if trigger[0]["type"] == "CONTACT_PROPERTY_NAME":
                mapped_value = owner_id_check(trigger[1]["id"], trigger[0]["id"], "CONTACT")
                if isinstance(mapped_value, dict):
                    print("Error: owner id substitution failed. This error was logged.")
                    logger.log_event("skipped_reenrollment_trigger", {"type":"CONTACT_PROPERTY_NAME", "detail": "substitution failure ownerId"})
                else:
                    processed_trigger = trigger
                    processed_trigger[1]["id"] = mapped_value
            else:
                assert trigger[0]["type"] == "FORM"
                assert trigger[1]["type"] == "PAGE"
                mapped_page_id = get_target_id("pageId", trigger[1]["id"])
                if mapped_page_id is None:
                    logger.log_event("skipped_reenrollment_trigger", {"type":"FORM", "detail": "substitution failure pageId"})
                else:
                    if "id" in trigger[0]:
                        mapped_id = get_target_id("formId", trigger[0]["id"])
                        if mapped_id is None:
                            logger.log_event("skipped_reenrollment_trigger", {"type":"FORM", "detail": "substitution failure formId"})
                        else:
                            processed_trigger = trigger
                            processed_trigger[0]["id"] = mapped_id
                            processed_trigger[1]["id"] = mapped_page_id
                    else:
                        processed_trigger = trigger
                        processed_trigger[1]["id"] = mapped_page_id
        else:
            assert len(trigger) == 1
            if trigger[0]["type"] == "CONTACT_PROPERTY_NAME":
                processed_trigger = trigger
            elif trigger[0]["type"] == "DYNAMIC_LIST":
                mapped_id = get_target_id("listId", trigger[0]["id"])
                if mapped_id is None:
                    logger.log_event("skipped_reenrollment_trigger", {"type":"DYNAMIC_LIST", "detail": "substitution failure listId"})
                else:
                    processed_trigger = trigger
                    processed_trigger[0]["id"] = mapped_id
            elif trigger[0]["type"] == "FORM":
                if "id" in trigger[0]:
                    mapped_id = get_target_id("formId", trigger[0]["id"])
                    if mapped_id is None:
                        logger.log_event("skipped_reenrollment_trigger", {"type":"FORM", "detail": "substitution failure formId"})
                    else:
                        processed_trigger = trigger
                        processed_trigger[0]["id"] = mapped_id
                else:
                    processed_trigger = trigger
            elif trigger[0]["type"] == "PAGE_VIEW":
                processed_trigger = trigger
            elif trigger[0]["type"] == "EVENT":
                logger.log_event("skipped_reenrollment_trigger", {"type":"EVENT", "detail": "event id " + str(trigger[0]["id"])})
            elif trigger[0]["type"] == "INTEGRATIONS_TIMELINE_EVENT":
                logger.log_event("skipped_reenrollment_trigger", {"type":"INTEGRATIONS_TIMELINE_EVENT", "detail": "integration timeline event id " + str(trigger[0]["id"])})
            else:
                raise ValueError("Unknown reenrollment trigger type encountered.")
        if processed_trigger != []:
            processed_triggers.append(processed_trigger)
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