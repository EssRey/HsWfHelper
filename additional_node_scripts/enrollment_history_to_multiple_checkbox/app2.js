require('dotenv').config();
const fs = require('fs');
const axios = require('axios').default;
const targetHapiKey = process.env.HAPIKEY_TARGET;
const contactsByList = require('./results/contactsByList.json');

console.log(contactsByList);