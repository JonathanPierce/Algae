// Overall application component
var Application = React.createClass({
	getInitialState: function() {
		return {
			state: {
				page: "loading",
				args: {}
			}
		};
	},

	componentDidMount: function() {
		// Register the callback
		ViewState.start(this.updateState);
	},

	updateState: function(newState) {
		this.setState(newState);
	},

	renderContent: function() {
		var page = this.state.state.page;

		// Render the loading screen
		if(page === "loading") {
			return (
				<div className="simpleContent">loading...</div>
			);
		}

		// Render an error screen
		if(page === "error") {
			return (
				<div className="simpleContent">Something went wrong... try again...</div>
			);
		}

		// Render the import page
		if(page === "import") {
			return (
				<ImportPage data={this.state} />
			);
		}

		if(page === "spot check" || page === "evaluate") {
			return (
				<EvaluatePage data={this.state} />
			);
		}

		if(page === "analyze") {
			return (
				<AnalyzePage data={this.state} />
			);
		}
	},

	render: function() {
		var content = this.renderContent();

		return (
			<div className="algae">
				<PageHeader state={this.state.state} />
				<div className="content">
					{ content }
				</div>
			</div>
		)
	}
});

// Page header
var PageHeader = React.createClass({
	render: function() {
		var state = this.props.state;

		return (
			<div className="pageHeader noSelect">
				<div className="title" title="Like MOSS, but better!">Algae</div>
				{
					["Import", "Evaluate", "Analyze", "Spot Check"].map(function(navItem) {
						var classes = "navItem";
						var lowercase = navItem.toLowerCase();
						if(lowercase === state.page) {
							classes += " selected";
						}

						var nav = function() {
							ViewState.setState(lowercase, {});
						};

						return (
							<div className={classes} onClick={nav} key={navItem}>{ navItem }</div>
						);
					})
				}
			</div>
		);
	}
});

// Evaluation/spot check view
var EvaluatePage = React.createClass({
	render: function() {
		return (
			<div className="evaluatePage">
				<Sidebar data={this.props.data} />
				<CodeView data={this.props.data} />
			</div>
		);
	}
});

// Import page
var ImportPage = React.createClass({
	import: function() {
		ViewState.importCorpus(this.refs.inputBox.getDOMNode().value);
	},
	render: function() {
		return (
			<div className="importPage paddedPage">
				<h1>Import</h1>
				<p>You need to import data into the Algae results viewer before you can view it. Simple submit the name of the config file (typically config.json) that you want to view after running Algae on its entirety. Note that importing data will overwrite any old imported data.</p>
				<h5>corpus path:</h5>
				<div>
					<input type="text" ref="inputBox" placeholder="example: config.json" />
					<button onClick={this.import}>Go</button>
				</div>
				<br/>
				<h5>current corpus:</h5>
				<div>
					<textarea value={JSON.stringify(this.props.data.corpusData, null, 2)} readOnly="true" />
				</div>
			</div>
		);
	}
});

// Analyze page
var AnalyzePage = React.createClass({
	render: function() {
		return <div>Analyze page</div>;
	}
});

// Spot check import

// Sidebar
var Sidebar = React.createClass({
	getSidebarContent: function() {
		var data = this.props.data;
		var page = data.state.page;
		var args = data.state.args;

		// Do we need to import
		if(!data.corpusData) {
			return (
				<div>You need to import data first.</div>
			)
		}

		// Do we have a selected detector and assignment?
		if(typeof args.detector === 'undefined' || typeof args.assignment === 'undefined') {
			// Select the first one
			args.detector = 0;
			args.assignment = 0;

			// Update the UI
			ViewState.setState(page, args);

			return <noscript />;
		}

		// Do we have the proper clusters?
		var detector = data.corpusData.detectors[args.detector].name;
		var assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
		var clusterKey = ViewState.getClusterKey(false, assignment, detector);

		var clusters = data.clusterDB[clusterKey];
		if(!clusters) {
			return (
				<div>waiting for clusters...</div>
			);
		}

		// Do we have a selected cluster/students?
		if(typeof args.cluster === 'undefined') {
			// Select the first
			args.cluster = 0;
			args.students = [0,1]

			// Update the UI
			ViewState.setState(page, args);

			return <noscript />;
		}

		// We can now render the full sidebar!
		var cluster = clusters[args.cluster];
		return (
			<div>
				<AssignPicker data={data} />
				<ClusterPicker clusters={clusters} data={data} cluster={cluster} />
				<StudentPicker cluster={cluster} data={data} />
				<Ratings cluster={cluster} data={data} clusterKey={clusterKey} />
			</div>
		);

	},
	render: function() {
		var sidebarContent = this.getSidebarContent();

		return (
			<div className="sidebar left">
				{ sidebarContent }
			</div>
		);
	}
});

// Code view
var CodeView = React.createClass({
	getContent: function() {
		var data = this.props.data;
		var args = data.state.args;

		// Do we have everything we need?
		if(typeof args.detector === "undefined"
			|| typeof args.assignment === "undefined"
			|| typeof args.cluster === "undefined"
			|| typeof args.students === "undefined") {
			return (
				<div>waiting for information...</div>
			);
		}

		// Render a column for each student
		var detector = data.corpusData.detectors[args.detector].name;
		var assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
		var clusterKey = ViewState.getClusterKey(false, assignment, detector);
		var clusters = data.clusterDB[clusterKey];
		var cluster = clusters[args.cluster];

		if(!cluster) {
			return (
				<div className="simpleContent">Nothing to see here. Move along.</div>
			);
		}

		var displayClusters = [];
		for(var i = 0; i < args.students.length; i++) {
			if(cluster.members[args.students[i]]) {
				displayClusters.push(cluster.members[args.students[i]]);
			}
		}

		return displayClusters.map(function(member) {
			var path = data.corpusData.corpus_path + "../../" + member.student + "/" + assignment + "/" + cluster.file;
			var partner = member.partner ? member.partner : "no partner";
			var semester = member.semester;
			var headerString = member.student + " [" + semester + "] (" + partner + ")";

			return (
				<div className={"codeColumn" + (displayClusters.length > 1 ? "" : " wide")} key={path}>
					<div className="header">{ headerString }</div>
					<CodeText path={path} />
				</div>
			);
		});
	},
	render: function() {
		var codeViewContent = this.getContent();

		return (
			<div className="codeView right">
			{ codeViewContent }
			</div>
		);
	}
});

// Code text
var CodeText = React.createClass({
	getInitialState: function() {
		return {
			text: null
		}
	},
	componentDidMount: function() {
		this.getCode();
	},
	getCode: function() {
		var that = this;
		$.get("/file?path=" + this.props.path, function(code) {
			that.setState({
				text: code
			});
		}).fail(function() {
			that.setState({
				text: "something went wrong. :("
			});
		});
	},
	getHTML: function(text) {
		// Clean up the text in prep for display.
        text = text.replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;");
        text = text.replace(/ /g, "&nbsp;");
        text = text.replace(/</g, "&lt;");
        text = text.replace(/>/g, "&gt;")
        text = text.replace(/\n/g, "<br/>");
        
        return prettyPrintOne(text);
	},
	render: function() {
		var content = null;

		if(!this.state.text) {
			content = <div>loading...</div>;
		} else {
			var prettyHTML = this.getHTML(this.state.text);

			content = <div className="prettyprint code"><div dangerouslySetInnerHTML={{__html: prettyHTML}}></div></div>;
		}

		return (
			<div className="codeText">
				{ content }
			</div>
		);
	}
});

// Detector/assignment picker
var AssignPicker = React.createClass({
	switchDetector: function(e) {
		var data = this.props.data;
		var args = data.state.args;

		args.detector = e.target.selectedIndex;
		args.assignment = 0;
		args.cluster = 0;
		args.students = [0,1];

		ViewState.setState(data.state.page, args);
	},
	switchAssignment: function(e) {
		var data = this.props.data;
		var args = data.state.args;

		args.assignment = e.target.selectedIndex;
		args.cluster = 0;
		args.students = [0,1];

		ViewState.setState(data.state.page, args);
	},
	renderDetectorPicker: function() {
		var data = this.props.data;
		var corpusData = data.corpusData;
		var args = data.state.args;

		return (
			<select onChange={this.switchDetector} value={args.detector}>
			{
				corpusData.detectors.map(function(detector, index) {
					return (
						<option key={detector.name} value={index}>{detector.name}</option>
					);
				})
			}
			</select>
		);
	},
	renderAssignmentPicker: function() {
		var data = this.props.data;
		var corpusData = data.corpusData;
		var args = data.state.args;
		var detector = corpusData.detectors[args.detector];
		var assignments = detector.assignments;

		return (
			<select selectedIndex={args.assignment} onChange={this.switchAssignment} value={args.assignment}>
			{
				assignments.map(function(assignment, index) {
					return (
						<option key={assignment} value={index}>{assignment}</option>
					);
				})
			}
			</select>
		);
	},
	render: function() {
		var detectorPicker = this.renderDetectorPicker();
		var assignmentPicker = this.renderAssignmentPicker();

		return (
			<div className="assignPicker section">
				<h5>Detector/Assignment:</h5>
				{ detectorPicker }
				<br/>
				{ assignmentPicker }
			</div>
		);
	}
});

// Cluster picker/info
var ClusterPicker = React.createClass({
	handleSelectChange: function(e) {
		this.changeCluster(e.target.selectedIndex);
	},
	next: function() {
		var currentIndex = this.props.data.state.args.cluster;
		var nextIndex = Math.min(currentIndex + 1, this.props.clusters.length - 1);
		this.changeCluster(nextIndex);
	},
	prev: function() {
		var currentIndex = this.props.data.state.args.cluster;
		var nextIndex = Math.max(currentIndex - 1, 0);
		this.changeCluster(nextIndex);
	},
	changeCluster: function(index) {
		var data = this.props.data;
		var args = this.props.data.state.args;
		args.cluster = index;
		args.students = [0,1];

		ViewState.setState(data.state.page, args);
	},
	renderClusters: function(clusters, current) {
		return (
			<select onChange={this.handleSelectChange} value={current}>
				{
					clusters.map(function(cluster, index) {
						var evalString = cluster.evaluation === 0 ? "?" : (cluster.evaluation === 1 ? "+" : "-");
						var clusterString = "(" + evalString + ") cluster " + (index + 1) + " | " + cluster.members[0].student;
						return <option key={index} value={index}>{clusterString}</option>;
					})
				}
			</select>
		);
	},
	render: function() {
		var data = this.props.data;
		var clusters = this.props.clusters;
		var cluster = this.props.cluster;
		var args = data.state.args;

		if(clusters.length === 0) {
			return (
				<div className="section"><h5>No clusters for this assignment.</h5></div>
			);
		}

		var renderedClusters = this.renderClusters(clusters, args.cluster);

		return (
			<div className="clusterPicker section">
				<h5>Choose Cluster:</h5>
				{ renderedClusters }
				<br/>
				<div>
					<button onClick={this.prev}>Prev</button>
					<button onClick={this.next}>Next</button>
				</div>
				<br/>
				<div>{"Cluster: " + (args.cluster + 1) + "/" + clusters.length}</div>
				<div>{"Partners allowed: " + (cluster.allowPartners ? "True" : "False")}</div>
				<div>{"File: " + cluster.file}</div>
				<div>{"Score: " + cluster.score}</div>
			</div>
		);
	}
});

// Students list
var StudentPicker = React.createClass({
	renderFirst: function(cluster, students) {
		var second = students[1] || -1;
		var args = this.props.data.state.args;
		var page = this.props.data.state.page;

		function change(e) {
			args.students[0] = e.target.selectedIndex;
			ViewState.setState(page, args);
		}

		return (
			<select onChange={change} value={students[0]}>
				{
					cluster.members.map(function(member, index) {
						var disabled = index === second;

						return (
							<option key={member.student} value={index} disabled={disabled}>{member.student}</option>
						);
					})
				}
			</select>
		);
	},
	renderSecond: function(cluster, students) {
		if(cluster.members.length < 2) {
			return <noscript />;
		}

		var first = students[0];
		var args = this.props.data.state.args;
		var page = this.props.data.state.page;

		function change(e) {
			args.students[1] = e.target.selectedIndex;
			ViewState.setState(page, args);
		}

		return (
			<select onChange={change} value={students[1]}>
				{
					cluster.members.map(function(member, index) {
						var disabled = index === first;

						return (
							<option key={member.student} value={index} disabled={disabled}>{member.student}</option>
						);
					})
				}
			</select>
		);
	},
	render: function() {
		var cluster = this.props.cluster;
		var students = this.props.data.state.args.students;

		if(!cluster) {
			return <noscript/>;
		}

		var first = this.renderFirst(cluster, students);
		var second = this.renderSecond(cluster, students);

		return (
			<div className="studentPicker section">
				<h5>Select students:</h5>
				{ first }
				{ second }
				<br/><br/>
				<div>{cluster.members.length + " students"}</div>
			</div>
		);
	}
});

// Ratings buttons
var Ratings = React.createClass({
	setCheating: function() {
		var index = this.props.data.state.args.cluster;

		if(this.props.cluster.evaluation === 1) {
			ViewState.setCluster(this.props.clusterKey, index, 0);
		} else {
			ViewState.setCluster(this.props.clusterKey, index, 1);
		}
	},
	setFalsePos: function() {
		var index = this.props.data.state.args.cluster;

		if(this.props.cluster.evaluation === 2) {
			ViewState.setCluster(this.props.clusterKey, index, 0);
		} else {
			ViewState.setCluster(this.props.clusterKey, index, 2);
		}
	},
	render: function() {
		var cluster = this.props.cluster;

		if(!cluster) {
			return <noscript />;
		}

		var cheatingClass = "cheating";
		var falsePosClass = "falsePos";
		if(cluster.evaluation === 1) {
			cheatingClass += " selected";
		}
		if(cluster.evaluation === 2) {
			falsePosClass += " selected";
		}

		return (
			<div className="ratings section">
				<h5>Evaluation:</h5>
				<button className={cheatingClass} onClick={this.setCheating}>Cheating</button>
				<button className={falsePosClass} onClick={this.setFalsePos}>False Pos</button>
			</div>
		);
	}
});

// Export button

// Export view