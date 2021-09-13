# Migration of Static Lists 
> Recreate all static lists from US-portal in EU-portal
> and fill them with the same contacts

## Setup

1. Install dependencies via **npm install**"**

2. Add HAPIKEY_ORIGIN variable (for US-Portal) and HAPIKEY_TARGET variable (for EU-Portal) in .env file (in the project root folder).
Structure: 
*HAPIKEY_ORIGIN=xxxxx-xxxx-...*

## Execution

1. Run *node app.js* in terminal.

This will get all properties from the target portal and store them in *Portal_Migration_JSON/reference_properties.json*, and store all owner-type properties as *Portal_Migration_JSON/reference_owner_properties.json*

This file is later used by another script

