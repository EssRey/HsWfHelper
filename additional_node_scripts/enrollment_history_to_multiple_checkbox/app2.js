require('dotenv').config();
const fs = require('fs');
const axios = require('axios').default;
const targetHapiKey = process.env.HAPIKEY_TARGET;
const wfsData = require('./results/contactsByList');

// Todo: Error handling, retries on rate limits (batch limited to 1000 contacts)

// consolidated concat func and create property function for one loop through contacts_by_list
const createPropConcatWFs = () => {

    const array = wfsData.contacts_by_list;
    const propertyOptions = [];

    // create obj with email: semicolon separated wfids (formatted to update multicheck property)
    const wfIdsByEmail = array.reduce((newObj, wfInstance) => {

        let wfId = Object.keys(wfInstance)[0]; 

        // push wfids as options in multicheck property
        propertyOptions.push({"label": wfId, "value": wfId});

            wfInstance[wfId].forEach(contact => {

                if (wfInstance[wfId].length) {

                    let email = contact['identity-profiles'][0].identities[0].value;

                    newObj.hasOwnProperty(email) ? newObj[email] = newObj[email] += `;${wfId}` : newObj[email] = wfId;
                }
                
            });
        
        return newObj;
        
    }, {});

    // obj to create multicheck property with wfids as options
    const propertyObj = {
        "name": "workflow_ids",
        "label": "Workflow IDs",
        "description": "All workflow IDs (flowId_id) from origin portal",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "checkbox",
        "hidden": false,
        "options": propertyOptions,
        "formField": false
    };

    // create custom property in target portal
    // Todo: Check if property exists? 

    axios.post(`https://api.hubapi.com/properties/v1/contacts/properties?hapikey=${targetHapiKey}`, propertyObj)
        .then(res => {
            console.log(res);
        })
        .catch(e => {
            console.log(e);
        });

    return wfIdsByEmail;
}

const updatePropertyByEmail = async () => {

    const wfIdsByEmail = await createPropConcatWFs();

    if (!Object.keys(wfIdsByEmail).length) {

        throw new Error('No contacts to update');
    }

    let targetPortalContactsToUpdate = [];

    for (key in wfIdsByEmail) {
        targetPortalContactsToUpdate.push({
            "email": key,
            "properties": [
                {
                    "property": "workflow_ids",
                    "value": wfIdsByEmail[key]
                }
            ]
        });
    }    

    axios.post(`https://api.hubapi.com/contacts/v1/contact/batch/?hapikey=${targetHapiKey}`, targetPortalContactsToUpdate)
        .then(res => {
            console.log(res);
        })
        .catch(e => {
            console.log(e);
        });
}

updatePropertyByEmail();