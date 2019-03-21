const express = require('express');
const app = express();


app.get('/', (req, res) =>{
	res.send({'hello': 'there'});
});

const PORT = process.env.PORT || 5001;

// app.listen(PORT);

app.listen(PORT, function () {
  console.log('Express server is up on port ' + PORT);
});