var ViewState = (function() {
	// Data members
	var corpusData = null;
	var spotData = null;
	var clusterDB = {};
	var cb = null;
	var state = {
		page: "spot",
		args: null
	};

	// Functions
	var flush = function() {
		cb({
			state: state,
			corpusData: corpusData,
			spotData: spotData,
			clusterDB: clusterDB
		});
	};

	var start = function(callback) {
		// Download the corpus data

		// Download the clusters

		// If present, set the page to evaluate

		// Otherwise, set to import

		// Install the cb
		cb = callback;

		// Flush the data
		flush();
	};

	var importCorpus = function() {
		// Have the server perform the corpus import process

		// Get the new corpus data JSON (by calling start again)
		start(cb);
	};

	var setSpotData = function(corpusPath, assignment, file) {
		// Set the spot data
		spotData = {
			corpusPath: corpusPath,
			assignment: assignment,
			file: file
		};

		// Downlaod the clusters

		// Update the cluster DB

		// Flush
		flush();
	};

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

		// If not a spot check, send to server

		// Flush changes back
		flush();
	}

	// return out an interface
	return {
		start: start,
		importCorpus: importCorpus,
		setSpotData: setSpotData,
		setState: setState,
		getClusterKey: getClusterKey,
		setCluster: setCluster
	};

})();