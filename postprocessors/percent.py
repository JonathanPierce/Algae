# Postprocessed pair results by calculating mean/std. deviation, and finding approrpaite outliers.
# assignment args:
# - see processor/edit_distance.py
# - alternatively, just use a files list
# postprocessor args:
# - sourceSuffix (string) - Suffix used by the processor.
# - resultsSuffix (string) - Suffix used by the postprocessor.
# - percent (number [0-100]) - Percentage of data to keep
# - top (bool): Take the top or bottom percent.

import helpers.common as common
import helpers.io as io
from multiprocessing import Process
import math

# converts a JSON pair result into a Python object
def pairJSONToObject(json):
	student1 = json["pair"][0]
	student2 = json["pair"][1]
	score = float(json["score"])
	return common.PairResult(student1, student2, score)

# creates clusters from the filtered data
def createClusters(data, filename, assignName, allowPartners, helpers):
	clusters = []

	for element in data:
		cluster = common.Cluster(allowPartners, filename, element.score)

		member1 = common.Member(element.pair[0], assignName, helpers)
		member2 = common.Member(element.pair[1], assignName, helpers)

		cluster.add(member1)
		cluster.add(member2)

		clusters.append(cluster)

	return clusters

def sortFun(a, b):
	return int(a.score - b.score)

# runs an entry in parellel
def runEntry(filename, students, helpers, assignment, args, allowPartners):
	# get the data
	assignName = assignment.name
	sourceSuffix = args["sourceSuffix"]
	resultsSuffix = args["resultsSuffix"]
	percent = float(args["percent"]) / 100.0
	top = args["top"]

	safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
	filepath = helpers.getProcessedPath(assignName, safeFilename)

	if filepath != None:
		rawJSON = io.readJSON(filepath)
		if rawJSON != None:
			data = []

			# convert into python objects
			for element in rawJSON:
				data.append(pairJSONToObject(element))

			# sort them
			data.sort(sortFun)

			# take to the top bottom percent
			takeNum = math.floor(float(len(data)) * percent)
			if "maxResults" in args:
				takeNum = min(args["maxResults"], takeNum)

			results = None
			if top:
				takeNum = int(takeNum * -1)
				results = data[takeNum:]
			else:
				results = data[:int(takeNum)]

			# create the clusters
			clusters = createClusters(results, filename, assignName, allowPartners, helpers)

			# flush to disk
			common.clustersToStandardJSON(clusters, assignName, common.makeFilenameSafe(filename) + resultsSuffix, helpers)

			# all done!
			helpers.printf("Finished '{}', with {} results!\n".format(assignName, len(clusters)))


# the main function
def run(students, assignments, args, helpers):
	# threads to join later
	threads = []

	# for each assignment
	for assignment in assignments:
		# for each entry
		assignName = assignment.name
		allowPartners = assignment.args["allowPartners"]

		# print progress
		helpers.printf("postprocessing '{}' in parellel...\n".format(assignName))

		# allow entry lists and file lists
		entries = []
		if assignment.args.has_key("entries"):
			entries = assignment.args["entries"]
		else:
			if assignment.args.has_key("files"):
				entries = assignment.args["files"]

		for entry in entries:
			# use the first source as the filename in case fo an entry
			filename = entry
			if assignment.args.has_key("entries"):
				filename = entry["sources"][0]

			# create the thread
			t = Process(target=runEntry, args=(filename, students, helpers, assignment, args, allowPartners))
			threads.append(t)
			t.start()

	# join all of the threads
	for t in threads:
		t.join()

	# all done
	return True