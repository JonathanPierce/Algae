var StudentIndex = (function() {
	var index = {};

	var add = function(student, assignment, detector, cluster) {
		if(!index[student]) {
			index[student] = {};
		}

		var studentData = index[student];
		if(!studentData[assignment]) {
			studentData[assignment] = {};
		}

		var assignData = studentData[assignment];
		if(!assignData[detector]) {
			assignData[detector] = [];
		}

		var detectData = assignData[detector];
		if(detectData.indexOf(cluster) === -1) {
			detectData.push(cluster);
		}
	};

	var remove = function(student, assignment, detector, cluster) {
		if(index[student] && index[student][assignment] && index[student][assignment][detector]) {
			var clusters = index[student][assignment][detector];
			var pos = clusters.indexOf(cluster);

			if(pos >= 0) {
				clusters.splice(pos, 1);
			}
		}
	};

	// Assignment and detector optional.
	var query = function(student, _assignment, _detector) {
		if(!_assignment && !_detector) {
			return index[student] || null;
		}

		if(!_detector && index[student]) {
			return index[student][_assignment] || null;
		}

		if(index[student] && index[student][_assignment]) {
			return index[student][_assignment][_detector] || null;
		}

		return null;
	};

	// Returns a string array of all detector names where detection is positive.
	var queryDetectors = function(members, assignment) {
		var detectors = [];

		for(var i = 0; i < members.length; i++) {
			var student = members[i].student;

			if(index[student] && index[student][assignment]) {
				var assignData = index[student][assignment];
				for(var key in assignData) {
					if(assignData.hasOwnProperty(key) && detectors.indexOf(key) === -1 && assignData[key].length > 0) {
						detectors.push(key);
					}
				}
			}

			var partner = members[i].partner;

			if(partner && index[partner] && index[partner][assignment]) {
				var assignData = index[partner][assignment];
				for(var key in assignData) {
					if(assignData.hasOwnProperty(key) && detectors.indexOf(key) === -1 && assignData[key].length > 0) {
						detectors.push(key);
					}
				}
			}
		}

		return detectors;
	}

	// Tells whether a cluster has cheating, based on the inverted index
	var hasCheating = function(cluster, assignment) {
		if(cluster.evaluation === 1) {
			return true;
		}

		if(cluster.evaluation === 2) {
			return false;
		}

		return queryDetectors(cluster.members, assignment).length > 0;
	}

	var reset = function() {
		index = {};
	};

	// Return out the interface
	return {
		add: add,
		remove: remove,
		query: query,
		queryDetectors: queryDetectors,
		hasCheating: hasCheating,
		reset: reset
	};
})();

var ViewState = (function() {
	// Data members
	var corpusData = null;
	var spotData = null;
	var clusterDB = {};
	var cb = null;
	var studentIndex = StudentIndex;
	var state = {
		page: "loading",
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
					clusterDB: clusterDB,
					studentIndex: studentIndex
				});
			});
		}
	};

	var start = function(callback) {
		// Install the cb
		cb = callback;

		// Reset the index
		studentIndex.reset();

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

						// Rebuild the index
						clusters.map(function(cluster) {
							if(cluster.evaluation === 1) {
								updateIndex(cluster.members, assign, detector.name, cluster, 1);
							}
						});

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

	var updateIndex = function(members, assign, detector, cluster, evaluation) {
		// Update the inverted index
		if(evaluation === 1) {
			// Do an add for each student and partner
			for(var i = 0; i < members.length; i++) {
				var member = members[i];

				studentIndex.add(member.student, assign, detector, cluster);

				if(member.partner) {
					studentIndex.add(member.partner, assign, detector, cluster);
				}
			}
		} else {
			// Do a remove for each student and partner
			for(var i = 0; i < members.length; i++) {
				var member = members[i];

				studentIndex.remove(member.student, assign, detector, cluster);

				if(member.partner) {
					studentIndex.remove(member.partner, assign, detector, cluster);
				}
			}
		}
	}

	var setCluster = function(clusterKey, index, evaluation) {
		// Update the DB
		clusterDB[clusterKey][index].evaluation = evaluation;

		// If not a spot check, send to server
		if(state.page === "evaluate") {
			var split = clusterKey.split("_");
			var detector = split[2];
			var assign = split[1];
			var cluster = clusterDB[clusterKey][index];
			var members = cluster.members;

			// Update the index
			updateIndex(members, assign, detector, cluster, evaluation);

			// Save to the server
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
