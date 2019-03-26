const chatbot = require('../chatbot/chatbot');

module.exports = app => {

    app.get('/', (req, res) => {
        console.log('dialogFlowRoutes "/" route');
        res.send({'hello': 'Fernanda'});
    });
    
    app.post('/api/df_text_query', async (req, res) =>{
        let responses = await chatbot.textQuery(req.body.text, req.body.parameters);
        res.send(responses[0].queryResult);
    });

    
    app.get('/api/df_event_query', async (req, res) =>{
        let responses = await chatbot.eventQuery(req.body.event, req.body.parameters);
        res.send(responses[0].queryResult);
    });
    
}