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

		// Render the import page
		if(page === "import") {
			return (
				<ImportPage data={this.state} />
			);
		}

		if(page === "spot check" && !this.state.spotData) {
			return (
				<SpotCheckImport data={this.state} />
			)
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

		if(page === "export") {
			return (
				<ExportPage data={this.state} />
			);
		}

		// Render an error screen
		return (
			<div className="simpleContent">Something went wrong... try again...</div>
		);
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
				<h5>config path:</h5>
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
var SpotCheckImport = React.createClass({
	import: function() {
		var config = this.refs.inputConfig.getDOMNode().value;
		var assign = this.refs.inputAssign.getDOMNode().value;
		var file = this.refs.inputFile.getDOMNode().value;

		ViewState.setSpotData(config, assign, file);
	},
	render: function() {
		return (
			<div className="spotCheckImport paddedPage">
				<h1>Spot Check Import</h1>
				<p>Spot checking is useful for tuning paremeters or other situations where you went to view results without doing a full import. Results are only saved in RAM, so be sure to export if you want to keep them.</p>
				<h5>config path:</h5>
				<input type="text" ref="inputConfig" placeholder="example: config.json" />
				<h5>assignment:</h5>
				<input type="text" ref="inputAssign" placeholder="example: Lab12" />
				<h5>postprocessed path:</h5>
				<input type="text" ref="inputFile" placeholder="example: obfuscation_results.json" />
				<br/><br/>
				<button onClick={this.import}>Go</button>
			</div>
		);
	}
});

// Sidebar
var Sidebar = React.createClass({
	getSidebarContent: function() {
		var data = this.props.data;
		var page = data.state.page;
		var args = data.state.args;

		// Do we need to import
		if(!data.corpusData && page === "evaluate") {
			return (
				<div>You need to import data first.</div>
			)
		}

		// Do we have a selected detector and assignment?
		if(page === "evaluate" && (typeof args.detector === 'undefined' || typeof args.assignment === 'undefined')) {
			// Select the first one
			args.detector = 0;
			args.assignment = 0;

			// Update the UI
			ViewState.setState(page, args);

			return <noscript />;
		}

		// Do we have the proper clusters?
		var detector, assignment, clusterKey;

		if(page === "evaluate") {
			detector = data.corpusData.detectors[args.detector].name;
			assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
			clusterKey = ViewState.getClusterKey(false, assignment, detector);
		}
		if(page === "spot check") {
			detector = data.spotData.file;
			assignment = data.spotData.assignment;
			clusterKey = ViewState.getClusterKey(true, assignment, detector);
		}

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
				<ExportSave data={data} clusters={clusters} />
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
		var page = data.state.page;

		// Do we have everything we need?
		if((typeof args.detector === "undefined" && data.state.page === "evaluate")
			|| (typeof args.assignment === "undefined" && data.state.page === "evaluate")
			|| typeof args.cluster === "undefined"
			|| typeof args.students === "undefined") {
			return (
				<div>waiting for information...</div>
			);
		}

		// Render a column for each student
		var detector, assignment, clusterKey;

		if(page === "evaluate") {
			detector = data.corpusData.detectors[args.detector].name;
			assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
			clusterKey = ViewState.getClusterKey(false, assignment, detector);
		}
		if(page === "spot check") {
			detector = data.spotData.file;
			assignment = data.spotData.assignment;
			clusterKey = ViewState.getClusterKey(true, assignment, detector);
		}

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
	text = text.replace(/\r/g, "<br/>"); // Windows, why???

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
		var data = this.props.data;

		if(data.state.page === "spot check") {
			return (
				<div className="assignPicker section">
					{
						"Spot checking " + data.spotData.file + " from " + data.spotData.assignment + "."
					}
				</div>
			);
		}

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
						cluster.evaluation = cluster.evaluation || 0; // For spot check
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
		var clusterIndex = data.state.args.cluster;

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
					<button onClick={this.prev} disabled={clusterIndex === 0}>Prev</button>
					<button onClick={this.next} disabled={clusterIndex === (clusters.length - 1)}>Next</button>
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
	getIndexInfo: function() {
		var data = this.props.data;
		var page = data.state.page;
		var args = data.state.args;
		var cluster = this.props.cluster;

		if(page === "spot check") {
			return null;
		}

		// Get info from the inverted index
		var detector = data.corpusData.detectors[args.detector].name;
		var assignment = data.corpusData.detectors[args.detector].assignments[args.assignment];
		var info = data.studentIndex.queryDetectors(cluster.members, assignment);

		// Remove the current detector
		var pos = info.indexOf(detector);
		if(pos >= 0) {
			info.splice(pos, 1);
		}

		// Render
		if(info.length === 0) {
			return null;
		}

		return (
			<div className="indexInfo">
				{
					"Member(s) of this cluster have been found to be cheating by detector" + (info.length > 1 ? "s: " : ": ") + info.join(", ") + "."
				}
			</div>
		);
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

		var indexInfo = this.getIndexInfo();

		return (
			<div className="ratings section">
				<h5>Evaluation:</h5>
				<button className={cheatingClass} onClick={this.setCheating}>Cheating</button>
				<button className={falsePosClass} onClick={this.setFalsePos}>False Pos</button>
				{ indexInfo }
			</div>
		);
	}
});

// Export/Save/Reimport button
var ExportSave = React.createClass({
	export: function() {
		ViewState.setState("export", {
			clusters: this.props.clusters
		});
	},
	reimport: function() {
		ViewState.unsetSpotData();

		var args = this.props.data.state.args;
		args.cluster = 0;
		ViewState.setState("spot check", args);
	},
	save: function() {
		$.get("/save", function() {});
	},
	render: function() {
		var data = this.props.data;
		var page = data.state.page;

		if(page === "evaluate") {
			return (
				<div className="exportSave section">
					<h5>Other options:</h5>
					<button onClick={this.save}>save data to disk</button>
					<button onClick={this.export}>export data</button>
				</div>
			)
		}

		if(page === "spot check") {
			return (
				<div className="exportSave section">
					<h5>Other options:</h5>
					<button onClick={this.reimport}>import new</button>
					<button onClick={this.export}>export data</button>
				</div>
			)
		}
	}
});

// Export view
var ExportPage = React.createClass({
	getText: function(clusters) {
		var final = [];

		// Get the cheating clusters
		for(var i = 0; i < clusters.length; i++) {
			var cluster = clusters[i];
			if(cluster.evaluation === 1) {
				final.push(cluster);
			}
		}

		// Get a unique student list for each semester
		var semesters = {};

		for(var i = 0; i < final.length; i++) {
			var members = final[i].members;

			for(var j = 0; j < members.length; j++) {
				var member = members[j];
				var semester = members[j].semester;

				if(!semesters[semester]) {
					semesters[semester] = [];
				}

				// Implicate the student
				if(semesters[semester].indexOf(member.student) === -1) {
					semesters[semester].push(member.student);
				}

				// Implicate the partner (if any)
				if(member.partner && semesters[semester].indexOf(member.partner) === -1) {
					semesters[semester].push(member.partner);
				}
			}
		}

		var obj = {};
		obj.count = final.length;
		obj.clusters = final;
		obj.students = semesters;
		return JSON.stringify(obj, null, 2);
	},
	render: function() {
		var clusters = this.props.data.state.args.clusters;

		var text = this.getText(clusters);

		return (
			<div className="exportPage paddedPage">
				<h1>Export Data</h1>
				<textarea defaultValue={text}/>
			</div>
		);
	}
});
