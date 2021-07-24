require('dotenv').config();
const fs = require('fs');
const axios = require('axios').default;
const originHapiKey = process.env.HAPIKEY_ORIGIN;

// Todo: Error handling

const getContactIdLists = async () => {

    const response = await axios.get(`https://api.hubapi.com/automation/v3/workflows/?hapikey=${originHapiKey}`);

    const workflowsData = response.data.workflows;

    if (!workflowsData.length) {

        throw new Error('Could not get workflows');
    }

    // console.log(workflowsData);

    // writeWfsFile(workflowsData);

    let contactListIds = [];

    for (workflow of workflowsData) {
        contactListIds.push({
            flowId_workflowId: `${workflow.migrationStatus.flowId}_${workflow.migrationStatus.workflowId}`,
            contactListIds: workflow.contactListIds
        });
    }    

    // console.log(contactListIdsArr);

    // writeContactListIdsFile(contactListIds);

    return contactListIds;

}

const getContactsByListId = async () => {

    const contactIdLists = await getContactIdLists();

    // loop through idLists and call list endpoints

    const result = await Promise.all(contactIdLists.map(workflow => {
        const listURL = `https://api.hubapi.com/contacts/v1/lists/${workflow.contactListIds.enrolled}/contacts/all?hapikey=${originHapiKey}`

        return axios.get(listURL)
            .then(res => {

                const key = workflow.flowId_workflowId;

                return {
                    [key]: res.data.contacts
                };
            }
        );
    }));

    writeContactsByListFile(result);

    return result;

}

getContactsByListId().then(res => {
    console.log(res);

    // loop through array and create property in target portal
    // multicheckbox with ALL workflow Ids
    
    // might roll this into a separate file

});

// Temp functions

function writeWfsFile(workflows) {
    let workflowsJson = {"workflows": workflows};
    testFile = JSON.stringify(workflowsJson, null, 2);
    fs.writeFileSync('results/workflows.json', testFile);
}

function writeContactListIdsFile(contactListIds) {
    let contactIdsJson = {"workflow_lists": contactListIds};
    testFile = JSON.stringify(contactIdsJson, null, 2);
    fs.writeFileSync('results/contactListIds.json', testFile);
}

function writeContactsByListFile(contactsByList) {
    let contactsByListJson = {"contacts_by_list": contactsByList};
    testFile = JSON.stringify(contactsByListJson, null, 2);
    fs.writeFileSync('results/contactsByList.json', testFile);
}

// Todo: One function for writing test files (Temp)

function writeJsonFile(objName, fileName, data) {

}