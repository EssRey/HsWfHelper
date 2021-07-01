# Program brief

## Motivation

A number of workflow actions are ambiguous in the way they appear in the Workflows API. For example, a "set property value" action will appear as a "SET_COMPANY_PROPERTY" action in the API whether it relates to a company, deal, ticket, quote, or conversation property.

For that reason, it is necessary to try and disambiguate these actions by checking the property name that is referenced in the workflow action.

The property names of the relevant object types are stored in a json configuration file (currently "../../reference_properties.json", but the output file should change)

## Program structure

### Inputs

This program is to take an api key from the "HAPIKEY_ORIGIN" environment variable that is contained in "../../.env" (this is the preferred implementation). Alternatively, it would be okay to use a separate ".env" file in this folder ("./.env" -- in that case, make sure to exclude that file from this repo via ".gitignore")

### Outputs

Make a number of http requests to the public CRM API (GET
/crm/v3/properties/{objectType} , https://developers.hubspot.com/docs/api/crm/properties ) to pull out lists of all existing properties for each of the five relevant object types.

Then format this data into a JSON string and write it to an output file (../../reference_properties_complete.json). That file should look like so (but including all properties):

```
{
    "company": [
        "name",
        "domain"
    ],
    "deal": [
        "createdate",
        "amount",
        "name"
    ],
    "ticket": [
        "createdate",
        "name"
    ],
    "quote": [
    ],
    "conversation": [
    ]
}
```

## Notes

1. Not sure if there may be a case where a "quote" or "conversation" object does not include (maybe some small or legacy license?) In that case, it would be safe to simply keep the property array associated with the particular object empty (just like in the sample json above).
2. For the time being, please ensure this program does not overwrite the existing "reference_properties.json" file ("../../reference_properties.json")
3. This program should abort if it encounters any errors (except if they can be resolved via retries etc.) -- a potentially-incomplete json file could create big problems down the road.
4. Philip -- can you please delete this very point (#4) as a pull request to test our collaboration flow? Thanks!