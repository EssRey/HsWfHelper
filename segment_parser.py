import json

###
# Configuration
###

test="test"
placeholder_property="message"

###
# Functions
###

def segment_processor(segment, owner_properties=["hubspot_owner_id"]):
    processed_segment = segment.copy()
    # process here
    #processed_segment = segment_placeholder(segment)
    return processed_segment



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
    if not isinstance(id_list, list):
        print("cannot parse reEnrollmentTriggerSets, returning empty segments")
        return []
    processed_triggers = []
    # process here
    return processed_triggers
