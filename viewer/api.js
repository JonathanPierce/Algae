var ViewState = (function() {
	// Data members
	var corpusData = null;
	var spotData = null;
	var clusterDB = {};
	var cb = null;
	var state = {
		page: "spot",
		args: {}
	};

	// Functions
	var flush = function() {
		if(cb) {
			window.requestAnimationFrame(function() {
				cb({
					state: state,
					corpusData: corpusData,
					spotData: spotData,
					clusterDB: clusterDB
				});
			});
		}
	};

	var start = function(callback) {
		// Install the cb
		cb = callback;

		// Download the corpus data
		$.get("/getcorpus", function(data) {
			corpusData = data;
			state.page = "evaluate";
			state.args = {};

			// Download the clusters
			corpusData.detectors.map(function(detector) {
				detector.assignments.map(function(assign) {
					// Grab the data
					var path = corpusData.corpus_path + detector.name + "/" + assign + "/clusters.json";
					var key = getClusterKey(false, assign, detector.name);

					$.get("/getclusters?path=" + path, function(clusters) {
						clusterDB[key] = clusters;

						// Flush the data
						flush();
					}).fail(function() {
						// Something went wrong.
						state.page = "error";
						state.args = {};
						flush();
					});
				});
			});
		}).fail(function() {
			console.log("Failed to retreive corpus info.");

			state.page = "import";
			state.args = {};

			flush();
		});
	};

	var importCorpus = function(path) {
		// Have the server perform the corpus import process
		$.get("/importcorpus?path=" + path, function(data) {
			// Get the new corpus data JSON (by calling start again)
			start(cb);
		});
	};

	var setSpotData = function(configPath, assignment, file) {
		// Get the config
		$.get("/file?path=" + configPath, function(config) {
			var path = config.corpusPath + "/__algae__/postprocessed/" + assignment + "/" + file;

			// Get the clusters
			$.get("/file?path=" + path, function(clusters) {
				// Update the cluster DB
				var clusterKey = getClusterKey(true, assignment, file);
				clusterDB[clusterKey] = clusters;

				// Set the spot data
				spotData = {
					corpusPath: config.corpusPath,
					assignment: assignment,
					file: file
				};

				// Flush
				flush();
			}).fail(function() {
				// Something went wrong.
				state.page = "error";
				state.args = {};
				flush();
			});
		}).fail(function() {
			// Something went wrong.
			state.page = "error";
			state.args = {};
			flush();
		});
	};

	var unsetSpotData = function() {
		spotData = null;
		flush();
	}

	var setState = function(page, args) {
		state = {
			page: page,
			args: args
		};

		flush();
	};

	var getClusterKey = function(fromSpot, assignment, detectorOrFilename) {
		var spotString = fromSpot ? "SPOT" : "CORPUS";

		return spotString + "_" + assignment + "_" + detectorOrFilename;
	};

	var setCluster = function(clusterKey, index, evaluation) {
		// Update the DB
		clusterDB[clusterKey][index].evaluation = evaluation;

		// If not a spot check, send to server
		if(state.page === "evaluate") {
			var split = clusterKey.split("_");
			var detector = split[2];
			var assign = split[1];

			var path = corpusData.corpus_path + detector + "/" + assign + "/clusters.json"
			$.get("/updatecluster?path=" + path + "&index=" + index + "&evaluation=" + evaluation, function(data) {
				// Do nothing.
			});
		}

		// Flush changes back
		flush();
	}

	// return out an interface
	return {
		start: start,
		importCorpus: importCorpus,
		setSpotData: setSpotData,
		unsetSpotData: unsetSpotData,
		setState: setState,
		getClusterKey: getClusterKey,
		setCluster: setCluster
	};

})();
