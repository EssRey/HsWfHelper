require('dotenv').config({ path: '../../.env'});
const axios = require('axios').default;
const targetHapiKey = process.env.HAPIKEY_TARGET;
const wfsData = require('./results/contactsByList');
const axiosRetry = require('axios-retry');

axiosRetry(axios, { 
    retries: 5,
    retryDelay: axiosRetry.exponentialDelay 
});

const timer = () => new Promise(res => setTimeout(res, 10000));

const delayMessage = async () => { 
    console.log('API Burst Limit reached... Pausing for 10 seconds')
    await timer();
    console.log('Resuming script');
}

const createProp = async () => {

    const propertyOptions = [];

    // create obj with email: semicolon separated wfids (formatted to update multicheck property)
    for (const wfInstance of wfsData) {

        let wfId = Object.keys(wfInstance)[0]; 

        // push wfids as options in multicheck property
        propertyOptions.push({"label": wfId, "value": wfId});

    };

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

        if (response.statusText === 'OK') console.log('Workflow IDs multi-checkbox property successfully created in portal--script complete.');

    } catch(error) {

        if (error.response.status === 409) console.log('Property already exists in target portal');

        // Todo: PUT options to update multicheck options here on 409
    }

}

createProp();
