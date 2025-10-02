// {fact rule=cross-site-scripting@v1.0 defects=1}
var express = require('express');
var app = express();

app.get('/', function (req, res) {
// defect
  res.send('Hello ' + eval(req.query.q));
  console.log(req.query.q);
});

app.listen(8080, function () {
  console.log('Example app listening on port 8080!');
// {/fact}
});