# Program brief

## Motivation

Workflow enrollment histories will be lost in the portal migration project. There are multiple reasons we need to preserve some of that information. In particular, we need to know which contact ever *enrolled* in which workflow. This is going to be essential information for solving particular problems around re-enrollment behavior in the target portal.

## Program structure

### Inputs

This program is to take an api key from the "HAPIKEY_ORIGIN" environment variable that is contained in "../../.env" (this is the preferred implementation). Alternatively, it would be okay to use a separate ".env" file in this folder ("./.env" -- in that case, make sure to exclude that file from this repo via ".gitignore")

In addition, program is (maybe optionally, see details below) to take a *second* api key (relating to the migration *target* portal) from the "HAPIKEY_TARGET" environment variable, same as before.

### Suggested processing sequence

1. Call the Workflows API to get all workflows (GET /automation/v3/workflows , https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows)

2. For each workflow, look at the list ID indicated by "contactListIds / "enrolled", and then look at the contacts in that list via Contact Lists API (GET /contacts/v1/lists/:list_id/contacts/all , https://legacydocs.hubspot.com/docs/methods/lists/get_list_contacts). Store vid and email address of every contact for every workflow/list

3. Ideally, write the output of 2 to a text file (json or csv or whatever). Preferably, this file will include for every contact "vid", "canonical-vid", the merged "merged-vids" array, and the email address.

(The next steps , or even just steps 5.-6., could be a separate program (using the file in 3. as input), or just a continuation of the program above)

4. Take the output of 2. or 3. and create an array of workflow_IDs for every *contact*. You will note that workflows actually have to IDs, "id" and "flowId". Please generate a synthetic string of the form "[flowId]_[id]" for this array.

5. create a multiple checkbox property in the *target* portal with all the possible "[flowId]_[id]" values.

6. Loop through all contacts in the target portal (identify them by email for simplicity) and set the value of the custom contact property created in 5. to all the values collected in 4.

### Output

See previous section

## Notes

1. This program should abort if it encounters any errors (except if they can be resolved via retries etc.) anywhere in steps 1 to 3 of the suggested sequence -- we need to be confident that we have a full list of historical enrollees of every contact-based workflow in the origin portal (otherwise we'll have a lot of problems down the road)
2. Some things in the suggested sequence haven't been tested much. It would be good to verify that the "enrolled" list really captures every contact who have ever enrolled in the workflow.
3. Importantly, it should be possible to run steps 1-3 or 1-4 separately from steps 5-6. Imagine that you may not have access to the two hapikeys at the same time -- you have access to the portal of origin first, so you run steps 1-3 or 1-4. Later you the target portal is ready, and you get a hapikey for the target portal, and then you want to run 5-6 or 4-6 using the output created in by steps 1-3 or 1-4 that were run before.
4. Sergio -- can you please delete this very point (#4) as a pull request to test our collaboration flow? Thanks!