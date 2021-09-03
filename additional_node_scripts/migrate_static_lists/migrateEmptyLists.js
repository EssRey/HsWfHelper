require('dotenv').config({ path: '../../.env'});
const apiKeyOrigin = process.env.HAPIKEY_ORIGIN;
const apiKeyTarget = process.env.HAPIKEY_TARGET;
const axios = require('axios');
const fs = require('fs');
const { url } = require('inspector');
let callCounter = 0;


//Format required endpoints
const getListsEndpoint = 'https://api.hubapi.com/contacts/v1/lists/static?hapikey=' + apiKeyOrigin; 
const createListEndpoint = 'https://api.hubapi.com/contacts/v1/lists?hapikey=' + apiKeyTarget;
let getContactsInListEndpoint = '';

//Sleeper function to pause execution, when burst limits are reached
const sleep = (ms) => {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < ms);
      
}

//Evaluates whether burst limit reached or not -> Calls sleeper function if burst limit reached
const countCalls = () => {
    if(callCounter == 95) {
        console.log('Burst limit reached. Pausing execution for 10 seconds');
        sleep(10000);
        return callCounter = 0;
    }else{
        return callCounter+=1;
    }
}

//
const getContactEmailsInList = async (uniqueListId) => {
    countCalls();
    getContactsInListEndpoint = `https://api.hubapi.com/contacts/v1/lists/${uniqueListId}/contacts/all?hapikey=${apiKeyOrigin}&property=email`;
    let res = await axios.get(getContactsInListEndpoint);
    let contactArray = res.data.contacts;
    let emailArray = [];
    let placeholderArray
    if (contactArray) emailArray = contactArray.map(contact => contact.properties.email ? contact.properties.email.value : "noEmail"); 
    vidOffset = res.data['vid-offset']; 
    while(res.data['has-more']) {
        countCalls();
        getContactsInListEndpoint = `https://api.hubapi.com/contacts/v1/lists/${uniqueListId}/contacts/all?hapikey=${apiKeyOrigin}&property=email&vidOffset=${vidOffset}`;
        res = await axios.get(getContactsInListEndpoint);
        contactArray = res.data.contacts;
        if (contactArray) placeholderArray = contactArray.map( contact => contact.properties.email ? contact.properties.email.value : "noEmail");
        emailArray = [...emailArray, ...placeholderArray];
        vidOffset = res.data['vid-offset'];
    }
    emailArray.sort((a,b) => a>b?1:-1);
    return emailArray;
}


/**
* Gets data for all static lists from origin portal
* @return {Object}       Object containing an array of objects. Each object within array represents one list with its data.
*/
const getStaticListsOrigin = async () => {     
    try {
        countCalls();
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
            countCalls();
            const res = await axios.post(createListEndpoint,{"name":`${listName}`}).then(countCalls());
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
const createListFiles = async (listIdArray) => {
    let uniqueListId = 0;
    for(let i=0; i<listIdArray.length; i++) {
        uniqueListId = listIdArray[i];
        const emailArray = await getContactEmailsInList(uniqueListId);
        fs.writeFileSync(`listsWithContacts/list_${uniqueListId}.txt`, emailArray.toString());
        console.log(i + ': Contact-File created successfully');
    }
}

//Execution 
getStaticListsOrigin()
    .then(data => cloneListsIntoTarget(data))
    .then(listIdArray => createListFiles(listIdArray));