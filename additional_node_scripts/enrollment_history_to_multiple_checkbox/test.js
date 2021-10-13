require('dotenv').config({ path: '../../.env'});
const fs = require('fs');
const axios = require('axios').default;
const originHapiKey = process.env.HAPIKEY_ORIGIN;
const axiosRetry = require('axios-retry');

axiosRetry(axios, { retries: 7 });

// Todo: Error handling

const timer = () => new Promise(res => setTimeout(res, 10000));

const delayMessage = async (listId) => { 
    console.log('API Burst Limit reached... Pausing for 10 seconds')
    await timer();
    console.log(`Resuming on list #${listId}`);
}

const getContactIdLists = async () => {

    try {
        const response = await axios.get(`https://api.hubapi.com/automation/v3/workflows/?hapikey=${originHapiKey}`);

        const workflowsData = response.data.workflows;
    
        if (!workflowsData.length) {
    
            throw new Error('Could not get workflows');
        }
    
        const contactListIds = [];
    
        for (workflow of workflowsData) {
            contactListIds.push({
                flowId_workflowId: `${workflow.migrationStatus.flowId}_${workflow.migrationStatus.workflowId}`,
                contactListIds: workflow.contactListIds
            });
        }    
    
        return contactListIds;

    } catch(error) {
        console.error(error);
    }

}

const getContactsByListId = async () => {

    const contactIdLists = await getContactIdLists();

    let limit = 100;

    let lastContacts, runningContacts;

    let workflowContacts = [];

    // loop through idLists and call list endpoints

    for (let i = 0; i < contactIdLists.length; i++) {

        const workflow = contactIdLists[i];

        let listURL = `https://api.hubapi.com/contacts/v1/lists/${workflow.contactListIds.enrolled}/contacts/all?hapikey=${originHapiKey}&count=100&vidOffset=`;

        try {
            console.log(`Getting contacts from list #${workflow.contactListIds.enrolled} (${(i + 1)} of ${contactIdLists.length})`);

            let response = await axios.get(listURL);

            let deleteProps = response.data.contacts.map(contact =>  {
                return { 
                    'vid': contact['vid'],
                    'canonical-vid': contact['canonical-vid'],
                    'merged-vids': contact['merged-vids'],
                    'identity-profiles': contact['identity-profiles'],
                    'merge-audits': contact['merge-audits'],
                } 
            });
    
            lastContacts = deleteProps;
    
            runningContacts = lastContacts;
    
            let offset = response.data['vid-offset'];
    
            limit = response.headers['x-hubspot-ratelimit-remaining'];
    
            // Paginate if 'has-more' = true with 'vid-offset'
    
            while (response.data['has-more']) {

                console.log(`List #${workflow.contactListIds.enrolled} 'has more: Still getting contacts...`);
    
                listURL = `https://api.hubapi.com/contacts/v1/lists/${workflow.contactListIds.enrolled}/contacts/all?hapikey=${originHapiKey}&count=100&vidOffset=${offset}`;
    
                response = await axios.get(listURL);
    
                lastContacts = response.data.contacts.map(contact =>  {
                    return { 
                        'vid': contact['vid'],
                        'canonical-vid': contact['canonical-vid'],
                        'merged-vids': contact['merged-vids'],
                        'identity-profiles': contact['identity-profiles'],
                        'merge-audits': contact['merge-audits'],
                    } 
                });
    
                runningContacts = [...runningContacts, ...lastContacts];
    
                offset = response.data['vid-offset'];
    
                limit = response.headers['x-hubspot-ratelimit-remaining'];
    
                // Pause execution for 10 seconds if rate limit remaining nears buffer (10 for testing)
    
                if (limit < 10) {
                    await delayMessage(workflow.contactListIds.enrolled);
                }
    
            }
        } catch(error) {
            console.log(`Could not get list ${workflow.contactListIds.enrolled}: ${error}`)
        }

        const key = workflow.flowId_workflowId;

        const workflowObj = {
            [key]: runningContacts
        }

        console.log(workflowObj[key].length);

        workflowContacts.push(workflowObj);

    }

    console.log(workflowContacts.length);

    try {
        writeContactsByListFile(workflowContacts);
    } catch(error) {
        console.error(error);
    }

    return workflowContacts;
}

getContactsByListId();

const writeContactsByListFile = contactsByList => {

    let out = "[";
        for (let i = 0; i < contactsByList.length-1; i++) {
                out+=JSON.stringify(contactsByList[i])+",";
            }
        out += JSON.stringify(contactsByList[contactsByList.length - 1]) + "]"
    // const contactsByListJson = {"contacts_by_list": contactsByList};
    // testFile = JSON.stringify(contactsByListJson);
    // fs.writeFile('results/contactsByList3.json', out, (error) => {
    //     if (error) {
    //         console.log(error);
    //     } else {
    //         console.log("File written successfully");
    //     }
    // });

    fs.writeFileSync('results/contactsByListTEST.json', out);

    console.log('File written successfully');
} 