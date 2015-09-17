var http = require('http');
var fs = require('fs');
var url = require('url');
var dirname = require('path').dirname;
var child_process = require('child_process');

// Maps paths to cluster JSON
var clusterCache = {};

// Function for logging errors
var error_log = function (err) {
    if (err) {
        console.log("Oops!");
        console.log(err);
    }
};

// Function for reading a file from disk
var get_file = function (path, callback) {
    fs.readFile(process.cwd() + "/" + path, function (err, data) {
        if (err) {
            error_log(err);
            callback(null);
            return;
        }
        
        // Return the data
        callback(data);
    })
};

// Gets a true MIME for a path
var get_mime = function (path) {
    if (/\.js$/.test(path)) {
        return "text/javascript";
    }
    if (/\.jsx$/.test(path)) {
        return "text/jsx";
    }
    if (/\.css$/.test(path)) {
        return "text/css";
    }
    if (/\.json$/.test(path)) {
        return "text/json";
    }
    if (/\.png$/.test(path)) {
        return "image/png";
    }
    if (/\.jpeg$/.test(path)) {
        return "image/jpeg";
    }

    // All else is plain text
    return "text/plain";
};

// Reads the current corpus JSON file
var get_corpus = function(callback) {
	get_file("import.json", function(data) {
		if(data) {
			return callback(JSON.parse(data));
		}

		callback(null);
	});
};

// Converts a job and assignmets list into a list of files
var get_file_list = function(job, assignment) {
	// helper functions
	function make_safe(path) {
		return path.replace(/\./g, "_") + "_";
	}
	function first_source(entry) {
		return make_safe(entry.sources[0]);
	}
	function process_filelist(list, suffix) {
		return list.map(function(member) {
			return assignment.name + "/" + make_safe(member) + suffix;
		});
	}
	function process_entries(list, suffix) {
		return list.map(function(member) {
			return assignment.name + "/" + first_source(member) + suffix;
		});
	}

	// Main job
	var processor_name = job.processor.name;

	if (processor_name == "obfuscation") {
		return [assignment.name + "/obfuscation_results.json"];
	}

	if(processor_name == "pairwise_identical") {
		return [assignment.name + "/" + job.processor.args.resultsSuffix]
	}

	// Get the results suffix from the postprocessor
	firstSuffix = "";
	for (var i = 0; i < job.postprocessors.length; i++) {
		if(job.postprocessors[i].args.resultsSuffix) {
			firstSuffix = job.postprocessors[i].args.resultsSuffix;
			break;
		}
	}

	// Process the entries or files
	if(assignment.args.files) {
		return process_filelist(assignment.args.files, firstSuffix);
	}
	if(assignment.args.entries) {
		return process_entries(assignment.args.entries, firstSuffix);
	}

	// Give up
	return [];
};

// Saves a file to disk synchronously
var save_sync = function(path, data) {
	var folder_path = dirname(path);
	child_process.spawnSync("mkdir", ["-p", folder_path]);
	fs.writeFileSync(path, data);
};

// Responders for requests at a given path.
var responders = {
    // Returns the file at ?path=path/to/file.ext
    "/file": function (req, res) {
        var parsed_url = url.parse(req.url, true);
        var file_path = parsed_url.query.path;
        
        if (file_path) {
            // Set the correct file type
            var file_type = get_mime(file_path);
            
            // Grab the file and return it
            get_file(file_path, function (data) {
                if (data) {
                    res.writeHead(200, { 'Content-Type': file_type });
                    res.end(data);
                } else {
                    // 404
                    responders["404"](req, res);
                }
                
            });
        } else {
            // 404
            responders["404"](req, res);
        }
    },
    
    // Return the home page HTML
    "/": function (req, res) {
        get_file("viewer/index.html", function (data) {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    },

    // Return a 404 page
    "404": function (req, res) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Hmm... it seems that we are unable to handle that request.\n');
    },

    // Import a corpus
    "/importcorpus": function(req, res) {
    	var parsed_url = url.parse(req.url, true);
        var config_path = parsed_url.query.path;

        // Read in the config
        get_file(config_path, function(config) {
        	if(config) {
        		var config = JSON.parse(config);
        		var corpus_path = config.corpusPath + "/__algae__/postprocessed/";

        		// Wipe out the old data
        		child_process.spawnSync("rm", ["-rf", config.corpusPath + "/__algae__/viewer"]);
        		clusterCache = {};

        		// Create the import.json data
        		var import_json = {};
        		import_json.detectors = [];

        		// For each job...
        		for (var i = 0; i < config.jobs.length; i++) {
        			var job = config.jobs[i];

        			// For each assignment...
        			for(var j = 0; j < job.assignments.length; j++) {
        				var assignment = job.assignments[j];

        				// Gather all files, read JSON, concatenate
        				var files_list = get_file_list(job, assignment);

        				var json = files_list.map(function(file) {
        					data = fs.readFileSync(corpus_path + file);
        					return JSON.parse(data);
        				});

        				var concatenated = json.reduce(function(prev, current) {
        					return prev.concat(current);
        				}, []);
 
				        // Add an evalaution metric
				        var complete = concatenated.map(function(data) {
				        	data.evaluation = 0;
				        	return data;
				        });

				        // Save in new location
				        var save_name = config.corpusPath + "/__algae__/viewer/" + job.name + "/" + assignment.name + "/clusters.json";
				        save_sync(save_name, JSON.stringify(complete));
        			}

        			// Update import.json
				    var detector = {};
				    detector.name = job.name;
				    detector.assignments = job.assignments.map(function(assign) {
				    	return assign.name;
				    });
				    import_json.detectors.push(detector);
        		}

		        // Update the corpus JSON
		        import_json.corpus_path = config.corpusPath + "/__algae__/viewer/";
		        var date = new Date();
		        import_json.date = date.toString();

		        // Save it
		        save_sync("import.json", JSON.stringify(import_json));

		        // Return 200
		        res.writeHead(200, {'Content-Type': 'text/json'});
        		res.end("{}");
        	} else {
        		// 404
        		responders["404"](req, res);
        	}
        });
    },

    // Request corpus info
    "/getcorpus": function(req, res) {
    	get_corpus(function(data) {
    		res.writeHead(200, { 'Content-Type': 'text/json' });
            res.end(JSON.stringify(data));
    	});
    },

    // Request clusters
    "/getclusters": function(req, res) {
    	var parsed_url = url.parse(req.url, true);
        var file_path = parsed_url.query.path;
        
        if (file_path) {
            // Set the correct file type
            var file_type = get_mime(file_path);
            
            // Grab the file and return it
            if(!clusterCache[file_path]) {
            	// Grab the file from disk
            	get_file(file_path, function (data) {
	                if (data) {
	                	// Cache the clusters
	                	clusters = JSON.parse(data);
	                	clusterCache[file_path] = clusters;

	                	// Return the JSON
	                    res.writeHead(200, { 'Content-Type': file_type });
	                    res.end(data);
	                } else {
	                    // 404
	                    responders["404"](req, res);
	                }  
	            });
            } else {
            	// Grab from the cache
            	text = JSON.stringify(clusterCache[file_path]);
            	res.writeHead(200, { 'Content-Type': file_type });
                res.end(text);
            }

        } else {
            // 404
            responders["404"](req, res);
        }
    },

    // Update cluster
    "/updatecluster": function(req, res) {
    	var parsed_url = url.parse(req.url, true);
        var file_path = parsed_url.query.path;
        var index = parseInt(parsed_url.query.index, 10);
        var evaluation = parseInt(parsed_url.query.evaluation, 10);

        if(file_path && typeof index !== 'undefined' && typeof evaluation !== "undefined") {
        	// If we are in the cache, just update
        	if (clusterCache[file_path]) {
        		clusterCache[file_path][index].evaluation = evaluation;
        		res.writeHead(200, {'Content-Type': 'text/json'});
        		res.end("{}");
        	} else {
        		// We should be in the cache. 404.
        		responders["404"](req, res);
        	}
        } else {
        	// 404
            responders["404"](req, res);
        }
    },

    "/save": function(req, res) {
    	save();

    	res.writeHead(200, {'Content-Type': 'text/json'});
        res.end("{}");
    }
};

// The main server listener
http.createServer(function (req, res) {
    var parsed_url = url.parse(req.url);
    
    var responder = responders[parsed_url.pathname];
    if (responder) {
        // Respond appropriately
        responder(req, res);
        return;
    }

    // Return a 404 if no responder was found
    responders["404"](req, res);
}).listen(1337);

// Set up exit listeners for clenaup
var cleanup = function() {
	console.log("\ncleaning up and exiting...");

	save();

	// Shutdown the server
	process.exit();
};

var save = function() {
	// Save the corpus cache to disk
	for (var path in clusterCache) {
		if(clusterCache.hasOwnProperty(path)) {
			save_sync(path, JSON.stringify(clusterCache[path]))
		}
	}
};

process.on("SIGINT", cleanup);
process.on("uncaughtException", cleanup);

// Ready to go!
console.log("Welcome to Algae Results Viewer!")
console.log("Visit http://localhost:1337 to view the application.")