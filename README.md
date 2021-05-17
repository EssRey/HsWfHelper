# HsWfHelper

[Intro text to come]

## Useful files in this repo

* "technical_limitations.md": a breakdown of what can be migrated with the current version of the public Workflows API
* "2_process_and_copy.py": the actual proof-of-concept migration script, with a lot of stub/dummy/simplification in it
* "action_schemata.json" contain processing schemata for all workflow action types

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
* (some additional IDs that haven't been tested yet, in particular stage and pipeline IDs, extensionIDs and extensionDefinitionIds, and appIds)

NOTE: Any mappings supplied as configuration are NOT being applied by the script yet (still being worked on)

## How to run

Run "2_process_and_copy.py" in a Python interpreter. Tested using Python 3.8.6 on MacOS 10.15.7 (note there are no actual tests yet).

NOTE: Right now the script will not in fact apply any ID mappings, and it will presume the existence of all properties. To run this script, please set the origin portal and the target portal api keys to the SAME key. The script will make copies of all workflows in the portal. This is obviously only safe in portals that exist for testing purposes only.

## Current limitations

In addition to the limitations laid out in "technical_limitations.md", right now the script has the following limitations:
* some "set property" actions and related actions are currently attributed to the wrong object type. See issue tracker, should be resolved in next version.
* "delay until time of day / day of week" actions are wrongly migrated as zero-delay "delay for set amount of time" actions (instead of as placeholders). See issue tracker. Should be trivially resolved in next version.
* no ID mappings are applied
* the following additional action types are migrated as placeholders:
  * webhook actions with request signatures
  * "rotate owner"
  * "create ticket" and "create deal" actions
  * workflow extension actions
* workflow enrollment triggers are not yet migrated (no automatic triggers in the migrated workflows, need to be added manually)
* every if-then filter condition is replaced with the dummy filter condition "create date is known", and would have to be corrected manually