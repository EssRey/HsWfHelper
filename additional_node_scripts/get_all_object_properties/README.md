# Migration of Static Lists 
> Recreate all static lists from US-portal in EU-portal
> and fill them with the same contacts

## Setup

1. Install dependencies via **npm install**"**

2. If not existing, create a **results** folder in *Portal_Migration_JSON*
Final structure: *Portal_Migration_JSON/results*

3. Add HAPIKEY_ORIGIN variable (for US-Portal) and HAPIKEY_TARGET variable (for EU-Portal) in .env file.
Structure: 
*HAPIKEY_ORIGIN=xxxxx-xxxx-...*

## Execution

1. Run *node app.js* in terminal.

This will get all properties from the target portal and store them in *Portal_Migration_JSON/results/object_properties.json*

This file is later used by another script

