# Migration of Static Lists 
> Recreate all static lists from US-portal in EU-portal
> and fill them with the same contacts

## Setup

1. Install dependencies via **npm install**"**

2. If not existing, create a **results** folder in *Portal_Migration_JSON*
Final structure: *Portal_Migration_JSON/results*

3. If not existing, create a **listsWithContacts** folder in *Portal_Migration_JSON/migrate_static_lists*
Final structure: *Portal_Migration_JSON/migrate_static_lists/listsWithContacts*

4. Ensure folder from 3 is empty

5. If not yet created, create **.env** file in *Portal_Migration_JSON*
Final structure: *Portal_Migration_JSON/.env*

6. Add HAPIKEY_ORIGIN variable (for US-Portal) and HAPIKEY_TARGET variable (for EU-Portal) in .env file.
Structure: 
*HAPIKEY_ORIGIN=xxxxx-xxxx-...*
*HAPIKEY_TARGET=xxxxx-xxxxx-...*

## Execution

1. Run *node migrateEmptyLists.js* in terminal.

This will get all static lists from US-Portal and all contacts in those lists. 
It will next re-create the static list in EU-Portal as empty lists.

2. Run *node addContactsToLists.js*. 

This will add all contacts to the respective static lists, via each contact's email address. 

