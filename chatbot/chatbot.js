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

const sessionPath = sessionClient.sessionPath(config.googleProjectId, config.dialogFlowSessionID);

module.exports = {
    textQuery: async function(text, parameters= {}){
        let self = module.exports;
        const request = {
            session: sessionPath,
            queryInput: {
                text: {
                    text: text,
                    languageCode: config.dialogFlowSessionLanguageCode,
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
        let self = module.exports;
        const request = {
            session: sessionPath,
            queryInput: {
                text: {
                    text: event,
                    parameters: structjson.jsonToStructProto(parameters),
                    languageCode: config.dialogFlowSessionLanguageCode,
                },
            }
        };
        let responses = await sessionClient.detectIntent(request)
        responses = await self.handleAction(responses);
        return responses;
    },
    handleAction: function(responses){
        return responses;
    }
}