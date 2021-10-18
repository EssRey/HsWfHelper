# What to expect after a migration via these scripts

High-level expectations and settings
- contact-based "standard" workflows are migrated as ACTIVE with a SHORT-CIRCUIT branch and an additional enrollment condition that will trigger in case of any prior enrollment in the same workflow in the origin portal
- contact-based "date-centered" and "date property based" workflows are migrated as INACTIVE, with no short-circuit and unmodified enrollment conditions
- "date-centered" workflows are centered on January 31st, 2022 (a correct future date needs to be set before activating the workflow)
- specific execution times (e.g. specific execution times/dates or dates the workflow will be scheduled to pause) in the settings of the workflow are not migrated
- The setting "When the contact no longer meets the enrollment conditions, remove them from the workflow?" is set to NO for every active workflow
- each migrated workflow should be error-free (though it be incomplete or include placeholders, see below)
- folder structure is lost, all migrated workflows/lists in root folder
- workflows and lists are not assigned to particular any teams (for content partitioning) after migration

a migrated workflow will have a one-to-one correspondence between workflow actions in the original and migrated workflow (though some of the actions may be placeholders in the migrated version, see below). There are the following EXCEPTIONS:
- a "short-circuit" ("create date is unknown") branch action which always evaluates to an empty branch will be inserted at the root of any migrated "standard" workflow. This action will have to be deleted manually to "go live" with the workflow. No to-do is created for this step.
- an if-then branching actions with more than two branches will miss its MIDDLE branches in the migrated versions. That is, only the first ("YES") condition and branch, as well the last ("NO") branch, will be migrated. This needs to be checked manually, and will be flagged as a to-do once per workflow.
- any "go to other action" (the one that connects branches) will be missing. This needs to be checked manually, and will be flagged as a to-do once per workflow.
- some migrated actions need to be checked manually for particular details. In those cases, a "TODO"-Placeholder with a description of the specific follow-up action is inserted before the action in question. It will also be flagged as a to-do each time.

Individual workflow actions will be migrated as follows:
- identical to the original action. Note that any "comment" attached to the action will be missing. In case of an if-then branch action, branch labels (which are purely cosmetic) will be missing.
- If the action cannot be recreated identically to the original action, a placeholder is created instead. The placeholder is a "Set [contact property] to [value] action, where "contact property" is the custom contact property created for this particular purpose ("action_placeholder_property" by default), and "value" will be an escaped rendition of the JSON representation of the action in the Workflows API. The placeholder needs to be replaced manually with an appropriate action. A to-do is created each time a placeholder substitutes an action.
- In a few cases, the workflow action can be migrated properly, but there is a small change it may miss some particular information or require a manual check for any reason. In that case the action is migrated, and an additional "TODO" placeholder action is inserted before it.

Filter conditions or "segments":
- "segments" occur in three places: as filter conditions in an active list, as automatic enrolment criteria in a workflow, or as a branch condition in an if-then branch workflow action. The following points apply to all of these cases.
- There will be a one-to-one correspondence between segments (i.e. individual conditions) in the original workflow or list and its migrated equivalent. "ILS" lists are the only exception to this rule (see below)
- If an individual segment cannot be re-created equivalently to its original form, it is replaced by a placeholder. The placeholder will take the form "[property] is any of [value], where "property" is one of the placeholder properties ("migration_placeholder_filter" / "migration_placeholder_deal_filter" / "hs_note_body" by default), and "value" is an escaped JSON representation of the segment in the Contact Lists API or Workflows API. The placeholder needs to be replaced manually with an appropriate segment. A to-do is created each time a placeholder substitutes a segment.

Re-enrolment triggers
- re-enrolment trigger conditions will either be migrated identically/correctly, or they will be skipped
- if a re-enrolment trigger is skipped, a to-do is created and it will have to be manually selected

"ILS" lists
- starting in end of July 2021, HubSpot lists use a different schema that is not backwards compatible with the way lists and other "segments" are rendered in HubSpot legacy APIs. Active lists that have been created or updated after ca. end of July 2021 will be returned in the new style by the Contact Lists API. This new style of filters cannot be parsed by this application at present. Such a list will therefore be migrated as an active list with ONE SINGLE PLACEHOLDER segment, where the placeholder uses the common placeholder format, and its value will be the escaped json of the "ilsFilterBranch" value. The entire list will have to be rebuild manually. A to-do is created in this case.
- workflow enrollment trigger conditions or if-then workfllow branch action conditions are not affected by this limitation
