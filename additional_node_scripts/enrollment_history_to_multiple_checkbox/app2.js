require('dotenv').config({ path: '../../.env'});
const axios = require('axios').default;
const targetHapiKey = process.env.HAPIKEY_TARGET;
const wfsData = require('./results/contactsByList');
const axiosRetry = require('axios-retry');

axiosRetry(axios, { retries: 5 });

const timer = () => new Promise(res => setTimeout(res, 10000));

const delayMessage = async () => { 
    console.log('API Burst Limit reached... Pausing for 10 seconds')
    await timer();
    console.log('Resuming script');
}

// consolidated concat func and create property function for one loop through contacts_by_list
const createPropConcatWFs = async () => {

    const array = wfsData.contacts_by_list;
    const propertyOptions = [];

    // create obj with email: semicolon separated wfids (formatted to update multicheck property)
    const wfIdsByEmail = array.reduce((newObj, wfInstance) => {

        let wfId = Object.keys(wfInstance)[0]; 

        // push wfids as options in multicheck property
        propertyOptions.push({"label": wfId, "value": wfId});

            wfInstance[wfId].forEach(contact => {

                if (wfInstance[wfId].length) {

                    // Find 'EMAIL' identity
                    let emailIndex = contact['identity-profiles'][0].identities.findIndex(identity => identity.type === 'EMAIL');

                    // If contact does not have an email, skip
                    if (emailIndex >= 0 ) {

                        let email = contact['identity-profiles'][0].identities[emailIndex].value;

                        newObj.hasOwnProperty(email) ? newObj[email] = newObj[email] += `;${wfId}` : newObj[email] = wfId;
                    }

                }
                
            });
        
        return newObj;
        
    }, {});

    // obj for create property POST request to create multicheck property with wfids as options
    const propertyObj = {
        "name": "pre_migration_workflow_enrollments",
        "label": "Legacy workflow enrollments",
        "description": "All workflow enrollments (flowId_id) in the origin portal",
        "groupName": "contactinformation",
        "type": "enumeration",
        "fieldType": "checkbox",
        "hidden": false,
        "options": propertyOptions,
        "formField": false
    };

    // create custom property in target portal

    try {
        let response = await axios.post(`https://api.hubapi.com/properties/v1/contacts/properties?hapikey=${targetHapiKey}`, propertyObj);

        if (response.statusText === 'OK') console.log('Workflow IDs property successfully created in portal');

    } catch(error) {

        if (error.response.status === 409) console.log('Property already exists in target portal');

        // Todo: PUT options to update multicheck options here on 409
    }

    return wfIdsByEmail;
}

const formatRequests = (wfIdsByEmail) => {

    let resultsArray = [];

    for (key in wfIdsByEmail) {
        resultsArray.push({[key]: wfIdsByEmail[key]});
    }

    let i = 0;
    //batchSize = contacts per API call (recommended MAX 100 per V1 endpoint docs)
    let batchSize = 100;
    let batchedContacts = [];

    while (i < resultsArray.length) {

        if (i % batchSize === 0) batchedContacts.push([]);
  
        batchedContacts[batchedContacts.length - 1].push(resultsArray[i++])
    }

    const requests = batchedContacts.map(array => {

        const spreadContactObjects = Object.assign({}, ...array);

        let targetPortalContactsToUpdate = [];

        for (key in spreadContactObjects) {
            targetPortalContactsToUpdate.push({
                "email": key,
                "properties": [
                    {
                        "property": "pre_migration_workflow_enrollments",
                        "value": spreadContactObjects[key]
                    }
                ]
            });
        }

        return targetPortalContactsToUpdate;

    });

    return requests;

}

const updatePropertyByEmail = async () => {

    const wfIdsByEmail = await createPropConcatWFs();

    if (!Object.keys(wfIdsByEmail).length) {

        throw new Error('No contacts to update');
    }

    const requests = formatRequests(wfIdsByEmail);

    let limit = 100;

    // Make API call for each batch of contacts (obj in array)

    for (let i = 0; i < requests.length; i++) {

        let contactBatch = requests[i];

        try {
            console.log(`Writing contacts to target portal (batch ${(i + 1)} of ${requests.length})`);

            let response = await axios.post(`https://api.hubapi.com/contacts/v1/contact/batch/?hapikey=${targetHapiKey}`, contactBatch);
    
            limit = response.headers['x-hubspot-ratelimit-remaining'];
    
            // Pause execution for 10 seconds if rate limit remaining nears buffer (10 for testing)
            if (limit < 10) {
                await delayMessage();
            }
        } catch(error) {
            console.log(`Could not post batch ${(i + 1)} of ${requests.length}: ${error}`);
        }

    }

    console.log('Contacts written to/updated in target portal. Script execution complete');
}

updatePropertyByEmail();
