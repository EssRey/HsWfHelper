# HsWfHelper

[Intro text to come]

## Useful files in this repo

* "technical_limitations.md": a breakdown of what can be migrated with the current version of the public Workflows API
* "actions_catalog.docx": a list of all workflow actions with sample JSON representations and some annotation
* "2_process_and_copy.py": the actual proof-of-concept migration script, with a lot of stub/dummy/simplification in it

## Configuration

### API keys

* Requires an ".env" file in the same directory as the ".py" file, with two lines containing api keys as follows (one for the portal of origin, and one for the destination portal):

  * `HAPIKEY_ORIGIN=f******d-2**v-4**5-9**3-7**********d`
  * `HAPIKEY_TARGET=6******5-3**2-4**4-b**1-***********4`

* THE DESTIONATION PORTAL MUST BE A TEST OR SANDBOX PORTAL (as this script currently produces a lot of placeholders and is not ready for serious use)

### Workflow action schemata

The schemata of individual workflow actions are defined in "actions_schemata.json". The keys of each action type correspond to all keys returned by the GET endpoints of the workflows API. Each key is mapped to one of the following processing actions:
* "PASS": The attribute will be written to the target portal with the same value that is read from the origin portal.
* "DROP": The attribute is not needed in the "Create Workflow" endpoint and is dropped.
* "SUBSTITUTE": When processing this attribute, the script will try and substitute references (IDs) contained in this attribute. If a substitution fails, the action is turned into a placeholder action.
* "NOT_IMPLEMENTED": If any attribute of an action has this value, the action is returned as a placeholder.

### ID mappings

The following ID mappings should be provided as a dictionary of dictionaries in the "id_mappings.json" file:
* workflowId
* emailContentId
* userId
* ownerId
* listId
* subscriptionId
* teamId

## How to run

Run "2_process_and_copy.py" in a Python interpreter. Tested using Python 3.8.6 on MacOS 10.15.7 (note there are no actual tests yet).