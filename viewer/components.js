// Overall application component
"use strict";

var Application = React.createClass({
	displayName: "Application",

	getInitialState: function getInitialState() {
		return {
			state: {
				page: "loading",
				args: {}
			}
		};
	},

	componentDidMount: function componentDidMount() {
		// Register the callback
		ViewState.start(this.updateState);
	},

	updateState: function updateState(newState) {
		this.setState(newState);
	},

	renderContent: function renderContent() {
		var page = this.state.state.page;

		// Render the loading screen
		if (page === "loading") {
			return React.createElement(
				"div",
				{ className: "simpleContent" },
				"loading..."
			);
		}

		// Render an error screen
		if (page === "error") {
			return React.createElement(
				"div",
				{ className: "simpleContent" },
				"Something went wrong... try again..."
			);
		}

		// Render the import page
		if (page === "import") {
			return React.createElement(ImportPage, { data: this.state });
		}

		if (page === "spot check" || page === "evaluate") {
			return React.createElement(EvaluatePage, { data: this.state });
		}

		if (page === "analyze") {
			return React.createElement(AnalyzePage, { data: this.state });
		}
	},

	render: function render() {
		var content = this.renderContent();

		return React.createElement(
			"div",
			{ className: "algae" },
			React.createElement(PageHeader, { state: this.state.state }),
			React.createElement(
				"div",
				{ className: "content" },
				content
			)
		);
	}
});

// Page header
var PageHeader = React.createClass({
	displayName: "PageHeader",

	render: function render() {
		var state = this.props.state;

		return React.createElement(
			"div",
			{ className: "pageHeader noSelect" },
			React.createElement(
				"div",
				{ className: "title", title: "Like MOSS, but better!" },
				"Algae"
			),
			["Import", "Evaluate", "Analyze", "Spot Check"].map(function (navItem) {
				var classes = "navItem";
				var lowercase = navItem.toLowerCase();
				if (lowercase === state.page) {
					classes += " selected";
				}

				var nav = function nav() {
					ViewState.setState(lowercase, {});
				};

				return React.createElement(
					"div",
					{ className: classes, onClick: nav, key: navItem },
					navItem
				);
			})
		);
	}
});

// Evaluation/spot check view
var EvaluatePage = React.createClass({
	displayName: "EvaluatePage",

	render: function render() {
		return React.createElement(
			"div",
			{ className: "evaluatePage" },
			React.createElement(Sidebar, { data: this.props.data }),
			React.createElement(CodeView, { data: this.props.data })
		);
	}
});

// Import page
var ImportPage = React.createClass({
	displayName: "ImportPage",

	"import": function _import() {
		ViewState.importCorpus(this.refs.inputBox.getDOMNode().value);
	},
	render: function render() {
		return React.createElement(
			"div",
			{ className: "importPage paddedPage" },
			React.createElement(
				"h1",
				null,
				"Import"
			),
			React.createElement(
				"p",
				null,
				"You need to import data into the Algae results viewer before you can view it. Simple submit the name of the config file (typically config.json) that you want to view after running Algae on its entirety. Note that importing data will overwrite any old imported data."
			),
			React.createElement(
				"h5",
				null,
				"corpus path:"
			),
			React.createElement(
				"div",
				null,
				React.createElement("input", { type: "text", ref: "inputBox", placeholder: "example: config.json" }),
				React.createElement(
					"button",
					{ onClick: this["import"] },
					"Go"
				)
			),
			React.createElement("br", null),
			React.createElement(
				"h5",
				null,
				"current corpus:"
			),
			React.createElement(
				"div",
				null,
				React.createElement("textarea", { value: JSON.stringify(this.props.data.corpusData, null, 2), readonly: "true" })
			)
		);
	}
});

// Analyze page
var AnalyzePage = React.createClass({
	displayName: "AnalyzePage",

	render: function render() {
		return React.createElement(
			"div",
			null,
			"Analyze page"
		);
	}
});

// Spot check import

// Sidebar
var Sidebar = React.createClass({
	displayName: "Sidebar",

	getSidebarContent: function getSidebarContent() {
		var data = this.props.data;
		var page = data.state.page;
		var args = data.state.args;

		// Do we need to import
		if (!data.corpusData) {
			return React.createElement(
				"div",
				null,
				"You need to import data first."
			);
		}

		// Do we have a selected detector and assignment?
		if (typeof args.detector === 'undefined' || typeof args.assignment === 'undefined') {
			// Select the first one
			args.detector = 0;
			args.assignment = 0;

			// Update the UI
			ViewState.setState(page, args);

			return React.createElement("noscript", null);
		}

		// Do we have the proper clusters?
		var detector = data.corpusData.detectors[args.detector].name;
		var assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
		var clusterKey = ViewState.getClusterKey(false, assignment, detector);

		var clusters = data.clusterDB[clusterKey];
		if (!clusters) {
			return React.createElement(
				"div",
				null,
				"waiting for clusters..."
			);
		}

		// Do we have a selected cluster?
		if (typeof args.cluster === 'undefined') {
			// Select the first
			args.cluster = 0;

			// Update the UI
			ViewState.setState(page, args);

			return React.createElement("noscript", null);
		}

		// Do we have selected student(s)?
		var cluster = clusters[args.cluster];
		if (!args.students || args.students.length === 0) {
			args.students = [];
			// Just add the first two (or, one, if necessary)
			for (var i = 0; i < Math.min(2, cluster.members.length); i++) {
				args.students.push(i);
			}

			// Update the UI
			ViewState.setState(page, args);

			return React.createElement("noscript", null);
		}

		// We can now render the full sidebar!
		return React.createElement(
			"div",
			null,
			React.createElement(AssignPicker, { data: data }),
			React.createElement(ClusterPicker, { clusters: clusters, data: data, cluster: cluster }),
			React.createElement(StudentPicker, { cluster: cluster, data: data }),
			React.createElement(Ratings, { cluster: cluster, data: data, clusterKey: clusterKey })
		);
	},
	render: function render() {
		var sidebarContent = this.getSidebarContent();

		return React.createElement(
			"div",
			{ className: "sidebar left" },
			sidebarContent
		);
	}
});

// Code view
var CodeView = React.createClass({
	displayName: "CodeView",

	render: function render() {
		return React.createElement("div", { className: "codeView right" });
	}
});

// Detector/assignment picker
var AssignPicker = React.createClass({
	displayName: "AssignPicker",

	switchDetector: function switchDetector(e) {
		var data = this.props.data;
		var args = data.state.args;

		args.detector = e.target.selectedIndex;
		args.assignment = 0;
		args.cluster = 0;

		ViewState.setState(data.state.page, args);
	},
	switchAssignment: function switchAssignment(e) {
		var data = this.props.data;
		var args = data.state.args;

		args.assignment = e.target.selectedIndex;
		args.cluster = 0;

		ViewState.setState(data.state.page, args);
	},
	renderDetectorPicker: function renderDetectorPicker() {
		var data = this.props.data;
		var corpusData = data.corpusData;
		var args = data.state.args;

		return React.createElement(
			"select",
			{ onChange: this.switchDetector },
			corpusData.detectors.map(function (detector, index) {
				var selected = index === args.detector;

				return React.createElement(
					"option",
					{ key: detector.name, selected: selected },
					detector.name
				);
			})
		);
	},
	renderAssignmentPicker: function renderAssignmentPicker() {
		var data = this.props.data;
		var corpusData = data.corpusData;
		var args = data.state.args;
		var detector = corpusData.detectors[args.detector];
		var assignments = detector.assignments;

		return React.createElement(
			"select",
			{ selectedIndex: args.assignment, onChange: this.switchAssignment },
			assignments.map(function (assignment, index) {
				var selected = index === args.assignment;

				return React.createElement(
					"option",
					{ key: assignment, selected: selected },
					assignment
				);
			})
		);
	},
	render: function render() {
		var detectorPicker = this.renderDetectorPicker();
		var assignmentPicker = this.renderAssignmentPicker();

		return React.createElement(
			"div",
			{ className: "assignPicker section" },
			React.createElement(
				"h5",
				null,
				"Detector/Assignment:"
			),
			detectorPicker,
			React.createElement("br", null),
			assignmentPicker
		);
	}
});

// Cluster picker/info
var ClusterPicker = React.createClass({
	displayName: "ClusterPicker",

	handleSelectChange: function handleSelectChange(e) {
		this.changeCluster(e.target.selectedIndex);
	},
	next: function next() {
		var currentIndex = this.props.data.state.args.cluster;
		var nextIndex = Math.min(currentIndex + 1, this.props.clusters.length - 1);
		this.changeCluster(nextIndex);
	},
	prev: function prev() {
		var currentIndex = this.props.data.state.args.cluster;
		var nextIndex = Math.max(currentIndex - 1, 0);
		this.changeCluster(nextIndex);
	},
	changeCluster: function changeCluster(index) {
		var data = this.props.data;
		var args = this.props.data.state.args;
		args.cluster = index;

		ViewState.setState(data.state.page, args);
	},
	renderClusters: function renderClusters(clusters, current) {
		return React.createElement(
			"select",
			{ onChange: this.handleSelectChange },
			clusters.map(function (cluster, index) {
				var selected = index === current;

				return React.createElement(
					"option",
					{ key: index, selected: selected },
					"cluster " + (index + 1)
				);
			})
		);
	},
	render: function render() {
		var data = this.props.data;
		var clusters = this.props.clusters;
		var cluster = this.props.cluster;
		var args = data.state.args;

		if (clusters.length === 0) {
			return React.createElement(
				"div",
				{ className: "section" },
				React.createElement(
					"h5",
					null,
					"No clusters for this assignment."
				)
			);
		}

		var renderedClusters = this.renderClusters(clusters, args.cluster);

		return React.createElement(
			"div",
			{ className: "clusterPicker section" },
			React.createElement(
				"h5",
				null,
				"Choose Cluster:"
			),
			renderedClusters,
			React.createElement("br", null),
			React.createElement(
				"div",
				null,
				React.createElement(
					"button",
					{ onClick: this.prev },
					"Prev"
				),
				React.createElement(
					"button",
					{ onClick: this.next },
					"Next"
				)
			),
			React.createElement("br", null),
			React.createElement(
				"div",
				null,
				"Cluster: " + (args.cluster + 1) + "/" + clusters.length
			),
			React.createElement(
				"div",
				null,
				"Partners allowed: " + (cluster.allowPartners ? "True" : "False")
			),
			React.createElement(
				"div",
				null,
				"File: " + cluster.file
			),
			React.createElement(
				"div",
				null,
				"Score: " + cluster.score
			)
		);
	}
});

// Students list
var StudentPicker = React.createClass({
	displayName: "StudentPicker",

	renderFirst: function renderFirst(cluster, students) {
		var second = students[1] || -1;
		var args = this.props.data.state.args;
		var page = this.props.data.state.page;

		function change(e) {
			args.students[0] = e.target.selectedIndex;
			ViewState.setState(page, args);
		}

		return React.createElement(
			"select",
			{ onChange: change },
			cluster.members.map(function (member, index) {
				var selected = index === students[0];
				var disabled = index === second;

				return React.createElement(
					"option",
					{ key: member.student, selected: selected, disabled: disabled },
					member.student
				);
			})
		);
	},
	renderSecond: function renderSecond(cluster, students) {
		if (cluster.members.length < 2) {
			return React.createElement("noscript", null);
		}

		var first = students[0];
		var args = this.props.data.state.args;
		var page = this.props.data.state.page;

		function change(e) {
			args.students[1] = e.target.selectedIndex;
			ViewState.setState(page, args);
		}

		return React.createElement(
			"select",
			{ onChange: change },
			cluster.members.map(function (member, index) {
				var selected = index === students[1];
				var disabled = index === first;

				return React.createElement(
					"option",
					{ key: member.student, selected: selected, disabled: disabled },
					member.student
				);
			})
		);
	},
	render: function render() {
		var cluster = this.props.cluster;
		var students = this.props.data.state.args.students;

		if (!cluster) {
			return React.createElement("noscript", null);
		}

		var first = this.renderFirst(cluster, students);
		var second = this.renderSecond(cluster, students);

		return React.createElement(
			"div",
			{ className: "studentPicker section" },
			React.createElement(
				"h5",
				null,
				"Select students:"
			),
			first,
			second,
			React.createElement("br", null),
			React.createElement("br", null),
			React.createElement(
				"div",
				null,
				cluster.members.length + " students"
			)
		);
	}
});

// Ratings buttons
var Ratings = React.createClass({
	displayName: "Ratings",

	setCheating: function setCheating() {
		var index = this.props.data.state.args.cluster;

		if (this.props.cluster.evaluation === 1) {
			ViewState.setCluster(this.props.clusterKey, index, 0);
		} else {
			ViewState.setCluster(this.props.clusterKey, index, 1);
		}
	},
	setFalsePos: function setFalsePos() {
		var index = this.props.data.state.args.cluster;

		if (this.props.cluster.evaluation === 2) {
			ViewState.setCluster(this.props.clusterKey, index, 0);
		} else {
			ViewState.setCluster(this.props.clusterKey, index, 2);
		}
	},
	render: function render() {
		var cluster = this.props.cluster;

		if (!cluster) {
			return React.createElement("noscript", null);
		}

		var cheatingClass = "cheating";
		var falsePosClass = "falsePos";
		if (cluster.evaluation === 1) {
			cheatingClass += " selected";
		}
		if (cluster.evaluation === 2) {
			falsePosClass += " selected";
		}

		return React.createElement(
			"div",
			{ className: "ratings section" },
			React.createElement(
				"h5",
				null,
				"Evaluation:"
			),
			React.createElement(
				"button",
				{ className: cheatingClass, onClick: this.setCheating },
				"Cheating"
			),
			React.createElement(
				"button",
				{ className: falsePosClass, onClick: this.setFalsePos },
				"False Positive"
			)
		);
	}
});

// Export button

// Export view
