require('dotenv').config();
const fs = require('fs');
const axios = require('axios').default;
const originHapiKey = process.env.HAPIKEY_ORIGIN;

// Todo: Error handling

const timer = () => new Promise(res => setTimeout(res, 10000));

const delayMessage = async (listId) => { 
    console.log('API Burst Limit reached... Pausing for 10 seconds')
    await timer();
    console.log(`Resuming on list #${listId}`);
}

const getContactIdLists = async () => {

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

        console.log(`Getting contacts from list #${workflow.contactListIds.enrolled} (${(i + 1)} of ${contactIdLists.length})`);

        let response = await axios.get(listURL);

        lastContacts = response.data.contacts;

        runningContacts = lastContacts;

        let offset = response.data['vid-offset'];

        limit = response.headers['x-hubspot-ratelimit-remaining'];

        // Paginate if 'has-more' = true with 'vid-offset'

        while (response.data['has-more']) {

            listURL = `https://api.hubapi.com/contacts/v1/lists/${workflow.contactListIds.enrolled}/contacts/all?hapikey=${originHapiKey}&count=100&vidOffset=${offset}`;

            response = await axios.get(listURL);

            lastContacts = response.data.contacts;

            runningContacts = [...runningContacts, ...lastContacts];

            offset = response.data['vid-offset'];

            limit = response.headers['x-hubspot-ratelimit-remaining'];

            // Pause execution for 10 seconds if rate limit remaining nears buffer (10 for testing)

            if (limit < 10) {
                await delayMessage(workflow.contactListIds.enrolled);
            }

        }

        const key = workflow.flowId_workflowId;

        const workflowObj = {
            [key]: runningContacts
        }

        workflowContacts.push(workflowObj);

    }

    writeContactsByListFile(workflowContacts);

    return workflowContacts;
}

getContactsByListId()

const writeContactsByListFile = contactsByList => {
    const contactsByListJson = {"contacts_by_list": contactsByList};
    testFile = JSON.stringify(contactsByListJson, null, 2);
    fs.writeFileSync('results/contactsByList.json', testFile);
}