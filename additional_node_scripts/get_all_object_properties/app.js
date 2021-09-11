require('dotenv').config({ path: '../../.env'});
const fs = require('fs');
const axios = require('axios').default;
const apiKey = process.env.HAPIKEY_ORIGIN;

//create api-call functions
const getCompanyProperties = () => {
       return axios.get(`https://api.hubapi.com/crm/v3/properties/companies?hapikey=${apiKey}`);
    }

const getDealProperties = () => {
    return axios.get(`https://api.hubapi.com/crm/v3/properties/deals?hapikey=${apiKey}`);
}

const getTicketProperties = () => {
    return axios.get(`https://api.hubapi.com/crm/v3/properties/tickets?hapikey=${apiKey}`);
}

const getQuoteProperties = () => {
    return axios.get(`https://api.hubapi.com/crm/v3/properties/quotes?hapikey=${apiKey}`);
}

const getLineItemProperties = () => {
    return axios.get(`https://api.hubapi.com/crm/v3/properties/line_item?hapikey=${apiKey}`);
}

let companyProperties = [];
let companyOwnerProperties = [];
let dealProperties = [];
let dealOwnerProperties = [];
let ticketProperties = [];
let ticketOwnerProperties = [];
let quoteProperties = [];
let quoteOwnerProperties = [];
let lineItemProperties = [];
let lineItemOwnerProperties = [];

//Run all api-calls --> Catch errors along the way, so promise.all will still resolve all functions
Promise.all([getCompanyProperties().catch(error => {console.log(error.response.status + " " + error.response.statusText); return "error"}), 
            getDealProperties().catch(error => {console.log(error.response.status + " " + error.response.statusText); return "error"}),
            getTicketProperties().catch(error => {console.log(error.response.status + " " + error.response.statusText); return "error"}), 
            getQuoteProperties().catch(error => {console.log(error.response.status + " " + error.response.statusText); return "error"}),
            getLineItemProperties().catch(error => {console.log(error.response.status + " " + error.response.statusText); return "error"})])
    .then((results) => {
        // If api-call successfull, create list of company properties
        if(results[0] !== "error"){
            const compRes = results[0].data;
            for (let i=0; i < compRes.results.length; i++) {
                companyProperties.push(compRes.results[i].name);
                if(compRes.results[i].referencedObjectType === "OWNER"){
                    companyOwnerProperties.push(compRes.results[i].name);
                }
            }
        }

        // If api-call successfull, create list of deal properties
        if(results[1] !== "error"){
            const dealRes = results[1].data;
            for (let i=0; i < dealRes.results.length; i++) {
                dealProperties.push(dealRes.results[i].name);
                if(dealRes.results[i].referencedObjectType === "OWNER"){
                    dealOwnerProperties.push(dealRes.results[i].name);
                }
            }
        }
        
        // If api-call successfull, create list of ticket properties
        if(results[2] !== "error"){
            const tickRes = results[2].data;
            for (let i=0; i < tickRes.results.length; i++) {
                ticketProperties.push(tickRes.results[i].name);
                if(tickRes.results[i].referencedObjectType === "OWNER"){
                    ticketOwnerProperties.push(tickRes.results[i].name);
                }
            }
       }
        
        // If api-call successfull, create list of quote properties
        if(results[3] !== "error"){
            const quotRes = results[3].data;
            for (let i=0; i < quotRes.results.length; i++) {
                quoteProperties.push(quotRes.results[i].name);
                if(quotRes.results[i].referencedObjectType === "OWNER"){
                    quoteOwnerProperties.push(quotRes.results[i].name);
                }
            }
        }

        // If api-call successfull, create list of product properties
        if(results[4] !== "error"){
            const lineRes = results[4].data;
            for (let i=0; i < lineRes.results.length; i++) {
                lineItemProperties.push(lineRes.results[i].name);
                if(lineRes.results[i].referencedObjectType === "OWNER"){
                    lineItemOwnerProperties.push(lineRes.results[i].name);
                }
            }
        }

        //creating JSON-Output and saving it to /results directory
        let finalJson = {"company": companyProperties, "deal": dealProperties, "ticket": ticketProperties, "quote": quoteProperties, "line_item": lineItemProperties};
        finalJson = JSON.stringify(finalJson, null, 2);
        fs.writeFileSync('../../reference_properties.json', finalJson);
        
        let finalOwnerJson = {"company": companyOwnerProperties, "deal": dealOwnerProperties, "ticket": ticketOwnerProperties, "quote": quoteOwnerProperties, "line_item": lineItemOwnerProperties};
        finalOwnerJson = JSON.stringify(finalOwnerJson, null, 2);
        fs.writeFileSync('../../reference_owner_properties.json', finalOwnerJson);
    });
