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

                newObj.hasOwnProperty(vid) ? newObj[vid] = newObj[vid] += `, ${wfId}` : newObj[vid] = wfId;
                
            });
        }
        
        return newObj;
        
    }, {});

    console.log(list);
}

concatWorkflowsByVid();