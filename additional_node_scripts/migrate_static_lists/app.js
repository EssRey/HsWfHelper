require('dotenv').config({ path: '../../.env'});
const apiKeyOrigin = process.env.HAPIKEY_ORIGIN;
const apiKeyTarget = process.env.HAPIKEY_TARGET;
const axios = require('axios');
const fs = require('fs');
const { url } = require('inspector');

//Format required endpoints
const getListsEndpoint = 'https://api.hubapi.com/contacts/v1/lists/static?hapikey=' + apiKeyOrigin; 
const createListEndpoint = 'https://api.hubapi.com/contacts/v1/lists?hapikey=' + apiKeyTarget;
let getContactsInListEndpoint = '';

  /**
   * Gets data for all static lists from origin portal
   * @return {Object}       Object containing an array of objects. Each object within array represents one list with its data.
   */
const getStaticListsOrigin = async () => {     
    try {
        const res = await axios.get(getListsEndpoint);
        const data = res.data;
        return data;
        
    } catch(err) {
         console.error(err);
    }
}

  /**
   * Recreates lists in target portal and creates a mappingJson.
   * @param  {Object} data  array of lists that are to be recreated.
   * @return {file}         listIdMapping.json in global results-directory.
   */
const cloneListsIntoTarget = async (data) => {
    let finalJson = '{\n';
    let listIdArray = [];

    for(let i=0; i<data.lists.length; i++) {
        let listName = data.lists[i].name;
        let listOldId= data.lists[i].listId;
        listIdArray.push(listOldId);
        try {
            const res = await axios.post(createListEndpoint,{"name":`${listName}`});
            listNewId = res.data.listId;
            finalJson = finalJson + `"${listOldId}":"${listNewId}", \n`;
            console.log(i+ ': List created successfully');
        } catch(err) {
            finalJson = finalJson + `"${listOldId}":ERROR, `;
            console.log(i + ': ' +err);
        } 
    }
    finalJson = finalJson.slice(0, -3) + '\n}';
    fs.writeFileSync('../../results/listIdMapping.json', finalJson); 
    return listIdArray;
}

// *** WRITE COMMENT ***  
const getContactsInList = async (listIdArray) => {
    let uniqueListId = 0;
    for(let i=0; i<listIdArray.length; i++) {
        uniqueListId = listIdArray[i];
        getContactsInListEndpoint = `https://api.hubapi.com/contacts/v1/lists/${uniqueListId}/contacts/all?hapikey=${apiKeyOrigin}`;
        const res = await axios.get(getContactsInListEndpoint);
        const contactArray = res.data.contacts;
        console.log(`Array generated for listID: ${listIdArray[i]}`);
        let vidStr = '[';
        if (contactArray.length > 0) {    
            for(let j=0; j<contactArray.length; j++) {
                vidStr = vidStr + `${contactArray[j].vid}, `;
            }
            vidStr = vidStr.slice(0, -2) + ']';
        } else {
            vidStr = '{"Error":"No contacts found in list"}';
        }
        fs.writeFileSync(`staticListsWithContacts/listID_${uniqueListId}.json`, vidStr);
    }
}

//Execution 
getStaticListsOrigin()
    .then(data => cloneListsIntoTarget(data))
    .then(listIdArray => getContactsInList(listIdArray));