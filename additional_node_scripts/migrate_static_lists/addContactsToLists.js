require('dotenv').config({ path: '../../.env'});
const apiKeyOrigin = process.env.HAPIKEY_ORIGIN;
const apiKeyTarget = process.env.HAPIKEY_TARGET;
const axios = require('axios');
const fs = require('fs');
const { url } = require('inspector');
let callCounter = 0;

const sleep = (ms) => {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < ms);
      
}

const countCalls = () => {
    if(callCounter == 95) {
        console.log('Burst limit reached. Pausing execution for 10 seconds');
        sleep(10000);
        return callCounter = 0;
    }else{
        return callCounter+=1;
    }
}

const listsArray = fs.readdirSync('listsWithContacts');
const idMapping = JSON.parse(fs.readFileSync('../../results/listIdMapping.json', 'utf8'));

contactArrays = listsArray
    .map(list => {
    const listId = list.substring(5, list.length - 4); 
    const contacts = fs.readFileSync(`listsWithContacts/${list}`, "utf8");
    return contacts ? [listId, contacts.split(',')] : 'empty';
    })
    .filter(list => list != 'empty')
    .sort((a, b) => a[0]-b[0])
    .forEach(async list =>  {
        let [listIdOld, emailArray] = list;
        emailArray = emailArray.filter(email => email != 'noEmail');
        const listIdNew = idMapping[`${listIdOld}`]
        const addContactsToListEndpoint = `https://api.hubapi.com/contacts/v1/lists/${listIdNew}/add?hapikey=${apiKeyTarget}`
        while(emailArray.length){
            const slicedEmailArray = emailArray.splice(0,500);
            const postBody = `{"emails": ${JSON.stringify(slicedEmailArray)}}`;
            try {
                countCalls();
                res = await axios.post(addContactsToListEndpoint, postBody, {headers: {'Content-Type': 'application/json'}});
            } catch(err){
                console.log(err);
            }
        }
    });


