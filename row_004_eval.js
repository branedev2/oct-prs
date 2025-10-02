// {fact rule=cross-site-scripting@v1.0 defects=1}
var express = require('express');
var app = express();
app.get('/', function(req, res) {
  var resp=eval("("+req.query.name+")");
// defect
  res.send('Response</br>'+resp);
});
app.listen(8000);

// {/fact}