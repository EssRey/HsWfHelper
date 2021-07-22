require('dotenv').config({ path: '../../.env'});
const apiKeyOrigin = process.env.HAPIKEY_ORIGIN;
const apiKeyTarget = process.env.HAPIKEY_TARGET;
const StaticList = require('./staticListConstructor');
const axios = require('axios');
const fs = require('fs');

//Format required endpoints
const getListsEndpoint = 'https://api.hubapi.com/contacts/v1/lists/static?hapikey=' + apiKeyOrigin;
const createListEndpoint = 'https://api.hubapi.com/contacts/v1/lists?hapikey=' + apiKeyTarget;

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
    let finalJson = '{\n'

    for(let i=0; i<data.lists.length; i++) {
        let listName = data.lists[i].name;
        let listOldId= data.lists[i].listId;
        try {
            const res = await axios.post(createListEndpoint,{"name":`${listName}`});
            listNewId = res.data.listId;
            finalJson = finalJson + `"${listOldId}":"${listNewId}", \n`
            console.log(i+ ': List created successfully');
        } catch(err) {
            finalJson = finalJson + `"${listOldId}":ERROR, `;
            console.log(i + ': ' +err);
        }
    }
    finalJson = finalJson.slice(0, -3) + '\n}';
    fs.writeFileSync('../../results/listIdMapping.json', finalJson);
}


//Execution 
getStaticListsOrigin()
    .then(data => cloneListsIntoTarget(data));
