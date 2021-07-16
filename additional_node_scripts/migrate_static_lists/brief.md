# Program brief

## Motivation

Static lists (unlike active lists) contain information about contacts and must therefore be preserved/migrated. In addition, they are referenced by workflows actions (in the "add to static list" and "remove from static list" actions), so they should be migrated before workflows in order to apply suitable ID substitutions during the workflow migration.

Migrating static lists should actually be able to happen in two stages that may not happen at the same time:

1. For each static list in the source portal, create a static lists with identical name in the target portal (and keep track of the mapping from old list ID to new list ID)
2. For each new static list in the target portal, add all the migrated contacts that were in the corresponding static list in the source portal

## Program structure

### Inputs

This program is to take an api key from the "HAPIKEY_ORIGIN" environment variable that is contained in "../../.env" (this is the preferred implementation). Alternatively, it would be okay to use a separate ".env" file in this folder ("./.env" -- in that case, make sure to exclude that file from this repo via ".gitignore"). This variable is used to authenticate requests to the migration source portal.

In addition, program takes a *second* api key (relating to the migration *target* portal) from the "HAPIKEY_TARGET" environment variable, same as before. This variable is used to authenticate requests to the migration target portal.

### Suggested program steps and outputs

#### PROGRAM STEP A

Get all lists in the source portal (e.g. via Contact Lists API). For every *static* list, create an identically-named static list in the *target* portal.

Store all source and target list IDs in a JSON string as in the folllowing example:

```
{
    "123": "456",
    "234": "567"
}
```

In this example, the source portal had two static lists with IDs 123 and 234. For list 123, an identically-named static list with ID 456 was created in the target portal. Similarly, the static list 567 in the target portal has the same name as the static list 234 in the source portal.

Write that JSON string to an output file (../../static_list_id_mapping.json).

Ideally, you would add that file to the ".gitignore" file in the root folder (it shouldn't end up in the Github repo)

#### PROGRAM STEP B

Read the "static_list_id_mapping.json" file from disk into an object.

For every static list in the source portal, get all contacts in the list by their primary email address.

Add the contact with the same email address in the target portal to the corresponding static list in the target portal (where the correspondence is provided by the data in "static_list_id_mapping.json").

## Notes

1. This program should *not* abort if it encounters any errors in accessing individual lists or contacts. Make sure to output appropriate console error messages (e.g. "couldn't recreate list 123", or "could not find contact test@test.com")
2. "Program step A" and "Program step B" should be able to run separately (though B obviously relies on the output produced by A), since some stuff (outside of this program) might need to happen in between these two steps.
3. If you wish to start working on this brief, can you please delete this very point (#3) via a pull request or via a direct edit to this repo? Thanks!