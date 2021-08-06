require('dotenv').config();
const fs = require('fs');
const axios = require('axios').default;
const targetHapiKey = process.env.HAPIKEY_TARGET;
const wfsData = require('./results/contactsByList');

// Should pull Email instead to POST to Target Portal 

const concatWorkflowsByVid = () => {
    const array = wfsData.contacts_by_list;

    const list = array.reduce((newObj, wfInstance) => {

        let wfId = Object.keys(wfInstance)[0]; 

        if (wfInstance[wfId].length) {
            wfInstance[wfId].forEach(contact => {
                let vid = contact.vid;
                // let email = contact['identity-profiles'][0].identities[0].value;

                newObj.hasOwnProperty(vid) ? newObj[vid] = newObj[vid] += `, ${wfId}` : newObj[vid] = wfId;
                // newObj.hasOwnProperty(email) ? newObj[email] = newObj[email] += `, ${wfId}` : newObj[email] = wfId;
                
            });
        }
        
        return newObj;
        
    }, {});

    console.log(list);
}

const createMulticheckProperty = () => {
    const propertyOptions = [];

    // TODO: Refactor - Already looping through contacts_by_list in concatWorkflowsByVid for wfId

    wfsData.contacts_by_list.forEach(wfInstance => {
        let wfId = Object.keys(wfInstance)[0];
        propertyOptions.push({"label": wfId, "value": wfId});
    })

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

    axios.post(`https://api.hubapi.com/properties/v1/contacts/properties?hapikey=${targetHapiKey}`, propertyObj)
        .then(res => {
            console.log(res);
        })
        .catch(e => {
            console.log(e);
        });
}

// concatWorkflowsByVid();
createMulticheckProperty();