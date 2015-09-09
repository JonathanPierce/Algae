# Postprocessed pair results by calculating mean/std. deviation, and finding approrpaite outliers.
# assignment args:
# - see processor/edit_distance.py
# - alternatively, just use a files list
# postprocessor args:
# - sourceSuffix (string) - Suffix used by the processor.
# - resultsSuffix (string) - Suffix used by the postprocessor.
# - deviation (number): the std. deviation of interest
# - minThreshold (number - optional): If the score above/below (depeding on "above") this value, always keep
# - above (bool): Whether we keep all those above or below this deviation.

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

# finds the mean of the data
def getMean(data):
	total = 0.0
	count = 0.0

	for element in data:
		total = total + element.score
		count = count + 1.0

	return total / count

# finds the std. deviation of the data
def getDeviation(data, mean):
	totalDiff = 0.0
	count = 0.0

	for element in data:
		totalDiff = totalDiff + (element.score - mean)**2.0
		count = count + 1.0

	normalized = totalDiff / count
	
	return math.sqrt(normalized)

# gets the z-score of a data point
def zScore(score, mean, deviation):
	return (score - mean) / deviation

# filters out result those that aren't suspicious
def filterData(data, mean, deviation, threshold, above, minThreshold):
	results = []

	for element in data:
		z = zScore(element.score, mean, deviation)

		if z <= threshold and not above:
			results.append(element)
			continue

		if z >= threshold and above:
			results.append(element)
			continue

		if minThreshold != None and element.score <= minThreshold and not above:
			results.append(element)
			continue

		if minThreshold != None and element.score >= minThreshold and above:
			results.append(element)
			continue

	return results

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

# runs an entry in parellel
def runEntry(filename, students, helpers, assignment, args, allowPartners):
	# get the data
	assignName = assignment.name
	sourceSuffix = args["sourceSuffix"]
	resultsSuffix = args["resultsSuffix"]
	threshold = assignment.args["threshold"]
	above = args["above"]
	minThreshold = None
	if assignment.args.has_key("minThreshold"):
		minThreshold = assignment.args["minThreshold"]

	safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
	filepath = helpers.getProcessedPath(assignName, safeFilename)

	if filepath != None:
		rawJSON = io.readJSON(filepath)
		if rawJSON != None:
			data = []

			# convert into python objects
			for element in rawJSON:
				data.append(pairJSONToObject(element))

			# get the mean
			mean = getMean(data)

			# get the deviation
			deviation = getDeviation(data, mean)
			helpers.printf("{}/{}: mean {}, deviation {}\n".format(assignName, filename, mean, deviation))

			# filter out data
			filtered = filterData(data, mean, deviation, threshold, above, minThreshold)

			# create the clusters
			clusters = createClusters(filtered, filename, assignName, allowPartners, helpers)

			# flush to disk
			common.clustersToStandardJSON(clusters, assignName, common.makeFilenameSafe(filename) + resultsSuffix, helpers)

			# all done!
			helpers.printf("Finished '{}'!\n".format(assignName))


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