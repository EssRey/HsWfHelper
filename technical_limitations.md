# Technical Limitations

Note that the following points are purely based on inspection of public and documented Workflows API endpoints.

## General limitations
* no non-contact workflows can be migrated

## Things that haven't been tested or clarified yet
* workflow extension actions untested
* all custom object dependencies are untested
* all dependencies on custom timeline events are untested
* there may be other custom dependencies that have not been tested (e.g. custom task types) that may result in additional nodes being migrated as placeholders only
* any of the newfangled "information passing between actions" logic (introduced in April 2021, and available in few actions at present) will likely be lost (not yet tested in detail)
* Enrollment triggers AND filters in if/then branching conditions haven't been evaluated yet. There will probably be some limits to what segmentation criteria can be fully migrated.
* suppression lists, automatic workflow unenrolllment settings, goal conditions, and other workflow-level settings have not been tested yet
* ad audience actions untested
* conversation object property actions untested (likely identical to quote object, i.e. only migrated as placeholder)

## Breakdown of workflow actions
The following list describes that can be migrated via API, based on inspection of public Workflows API endpoints. Note that the actual migration scripts are still work in progress.

### Actions that can be migrated
* "Add to static list"
* "Copy company property value"
* "Delay for a set amount of time"
* "Enroll in another workflow"
* "Increase or decrease property value"
* "Increase or decrease property value"
* "Manage subscription status"
* "Remove from static list"
* "Rotate record to owner"
* "Send email"
* "Send in-app notification"
  * owner property-based recipients may have to be re-added manually
* "Send internal marketing email"
  * the actual contents of the email may have to be recreated manually, not tested yet
* "Send internal SMS"
* "Trigger webhook"
  * in some cases, the request signature will have to be set manually

### Action that can only be migrated as a placeholder (need to be manually re-created)

* "Delay until a day or time"
* "Delay until event happens"
* "Custom code"
* "Format data"
* "Send internal email notification"
* "Set marketing contact status"

### Special cases
* "If/then branch"
  * Can be migrated, but all its "middle branches" (i.e. branches other than the first positive (formerly "YES") branch and the "NO" branch) must be manually recreated
* "Simple branch" (new in May 2021)
  * Can only be migrated as a placeholder, AND all its branches must be manually recreated
* "Create record"
  * deal and ticket migration actions can be migrated. Company creation action will be migrated as placeholder.
  * timeline backfill settings will have to be set manually
* "Set property value" / "Copy property value" / "Clear property value"
  * in case of a contact target property, the action can be migrated
  * in case of a deal/quote/ticket/conversation target property, the action will be migrated as placeholder
  * in case of a company target property, the action will be migrated if the property name is unambiguous (if there is no property with identical name in deal/ticket/quote/conversation objects, assuming those objects cannot be excluded from consideration); otherwise migrated as placeholder
* "Create task"
  * can usually be migrated, but tasks with "Sales Navigator" types will be migrated as placeholders
* "Go to action"
  * this workflow action cannot be migrated at all, even as a placeholder; it will have to be recreated manually after inspecting the individual origin workflows