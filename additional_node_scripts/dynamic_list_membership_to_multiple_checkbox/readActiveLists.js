require('dotenv').config({ path: '../../.env'});
const apiKeyOrigin = process.env.HAPIKEY_ORIGIN;
const apiKeyTarget = process.env.HAPIKEY_TARGET;
const axios = require('axios');
const fs = require('fs');
const { url } = require('inspector');
let callCounter = 0;


//Format required endpoints
const getListsEndpoint = 'https://api.hubapi.com/contacts/v1/lists/dynamic?count=250&hapikey=' + apiKeyOrigin; 
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
    getContactsInListEndpoint = `https://api.hubapi.com/contacts/v1/lists/${uniqueListId}/contacts/all?hapikey=${apiKeyOrigin}&property=email&count=100`;
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
* Gets data for all active lists from origin portal
* @return {Object}       Object containing an array of objects. Each object within array represents one list with its data.
*/
const getActiveListsOrigin = async () => {     
    try {
        countCalls();
        const res = await axios.get(getListsEndpoint);
        let listIdArray = [];
        for(let i=0; i< res.data.lists.length; i++) {
            listIdArray.push(res.data.lists[i].listId);
        }
        return listIdArray;
        
    } catch(err) {
         console.error(err);
    }
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
getActiveListsOrigin()
    .then(listIdArray => createListFiles(listIdArray));