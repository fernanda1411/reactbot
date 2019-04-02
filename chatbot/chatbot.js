'use strict'
const dialogflow = require('dialogflow');
const structjson = require('./structjson');
const config = require('../config/keys');

const projectId = config.googleProjectID;
const sessionId = config.dialogFlowSessionID;
const languageCode = config.dialogFlowSessionLanguageCode;


const credentials = {
    client_email: config.googleClientEmail,
    private_key: config.googlePrivateKey,
};

const sessionClient = new dialogflow.SessionsClient({projectId, credentials});
// const sessionClient = new dialogflow.SessionsClient({
//     keyFilename: '/Users/nanda/Projects/Project/reactbot/config/reactpageagent-b0ba4-6e906c102a3c.json'
// });
// const sessionClient = new dialogflow.SessionsClient();

// console.log('sessionClient', sessionClient);

const sessionPath = sessionClient.sessionPath(projectId, sessionId);

console.log('sessionPath: ', sessionPath);

module.exports = {
    textQuery: async function(text, parameters= {}){
        let self = module.exports;
        const request = {
            session: sessionPath,
            queryInput: {
                text: {
                    text: text,
                    languageCode: languageCode,
                },
            },
            queryParams: {
                payload: {
                    data: parameters
                }
            }
        };
        let responses = await sessionClient.detectIntent(request)
        responses = await self.handleAction(responses);
        return responses;
    },

    eventQuery: async function(text, parameters= {}){
        console.log('eventQueries')
        let self = module.exports;
        const request = {
            session: sessionPath,
            queryInput: {
                text: {
                    text: 'event',
                    parameters: structjson.jsonToStructProto(parameters),
                    languageCode: languageCode,
                },
            }
        };
        console.log('antes intent');
        let responses = await sessionClient.detectIntent(request);
        console.log('depois intent');
        responses = await self.handleAction(responses);
        return responses;
    },
    handleAction: function(responses){
        return responses;
    }
}