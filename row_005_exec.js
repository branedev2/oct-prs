// Use Express for serving the webpages
const express = require("express");

// To write to file
const fs = require('fs');
const { get } = require("http");

// Running a file
const { exec } = require('child_process');

// Initialisation
const app = express();
const port = 3000;

// Save functions and IDs in memory
var code = {}

// Use the EJS display engine
app.set("view engine", "ejs");

//body parser
app.use(
	express.urlencoded({
		extended: true,
	})
);

// Home page
app.get("/", (req, res) => {
	res.render("home");
});

// {fact rule=os-command-injection@v1.0 defects=1}
// Execute a function
app.get('/function/:id?', function(req , res){
		
	var output = ""

// defect
	exec(`node ./functions/${req.params.id}`, (error, stdout, stderr) => {
		if (error) {
		  console.error(`exec error: ${error}`);
		  return;
		}
		res.json({ output: stdout });
// {/fact}
	});
	
});

// Show functions
app.get('/functions', (req,res) => {
	res.render("table", {functions: code});
})

// Create new function
app.post("/post_function", (req, res) => {
	
	if (!req.body.code) {
		res.status(404, "Error. No code found.")
	}

	var random_id = (Math.random() + 1).toString(36).substring(7);

	fs.writeFile(`./functions/${random_id}`, req.body.code, err => {
		if (err) {
			res.status(404, "Error. No code found.")
		}
		// file written successfully
	});

	code[random_id] = req.body.code;

	res.redirect('/functions')

});

// Start serving
app.listen(port, () => {
	console.log(`Example app listening on port ${port}`);
});
