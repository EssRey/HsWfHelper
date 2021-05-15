# HsWfHelper

## Useful files in this repo
+ "technical_limitations.md": a breakdown of what can be migrated with the current version of the public Workflows API
* "actions_catalog.docx": a list of all workflow actions with sample JSON representations and some annotation
* "2_process_and_copy.py": a simple proof-of-concept migration script, with a lot of stub/dummy/simplification in it

## How to run

* Requires an ".env" file in the same directory as the ".py" file, with two lines containing api keys as follows (one for the portal of origin, and one for the destination portal):

  * `HAPIKEY_ORIGIN=f******d-2**v-4**5-9**3-7**********d`
  * `HAPIKEY_TARGET=6******5-3**2-4**4-b**1-***********4`

* THE DESTIONATION PORTAL MUST BE A TEST PORTAL (as this script currently produces a lot of placeholders and is not ready for serious use)

* Tested using Python 3.8.6 (not there are no actual tests yet)