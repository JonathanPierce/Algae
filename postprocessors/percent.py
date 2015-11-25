# Postprocessed pair results by calculating mean/std. deviation, and finding approrpaite outliers.
# assignment args:
# - see processor/edit_distance.py
# - alternatively, just use a files list
# postprocessor args:
# - sourceSuffix (string) - Suffix used by the processor.
# - resultsSuffix (string) - Suffix used by the postprocessor.
# - percent (number [0-100]) - Percentage of data to keep
# - top (bool): Take the top or bottom percent.
# - groupPairs (bool) - Cluster together connected components of pairs

import helpers.common as common
import helpers.io as io
from multiprocessing import Process
from guassian import getMean, getDeviation
import math
import gc

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
	if a.score < b.score:
		return -1
	return 1

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
		rawData = common.PairResults(assignName, safeFilename, helpers)
		data = []

		# convert into python objects
		i = 0
		for pair in rawData.iterate():
			data.append(pair)

			i += 1
			if i % 100000 == 0:
				gc.collect()

		# sort them
		data.sort(sortFun)

		# calculate and print stats
		mean = getMean(data)
		dev = getDeviation(data, mean)
		helpers.printf("{}/{} mean: {}, std. devation: {}\n".format(assignName, filename, mean, dev))

		# take to the top bottom percent
		takeNum = math.floor(float(len(data)) * percent)
		if "maxResults" in args:
			takeNum = min(args["maxResults"], takeNum)

		if top:
			data = data[::-1] # conveniently reverse

		results = []
		taken = 0
		index = 0
		while taken < takeNum:
			current = data[index]

			member1 = common.Member(current.pair[0], assignName, helpers)
			member2 = common.Member(current.pair[1], assignName, helpers)

			if allowPartners and member1.partner != None and member2.partner != None:
				if member1.student == member2.partner and member2.student == member1.partner:
					# student are partners, ignore
					index += 1
					continue

			# take this entry
			taken += 1
			index += 1
			results.append(current)

			if index % 50000 == 0:
				gc.collect()

		# create the clusters
		clusters = createClusters(results, filename, assignName, allowPartners, helpers)

		# group pairs if necessary
		if args.has_key("groupPairs") and args["groupPairs"] == True:
			clusters = common.groupPairClusters(clusters, top)

		# free up RAM
		gc.collect()

		# flush to disk
		common.clustersToStandardJSON(clusters, assignName, common.makeFilenameSafe(filename) + resultsSuffix, helpers)

		# all done!
		helpers.printf("Finished '{}/{}', with {} results!\n".format(assignName, filename, len(clusters)))


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
		helpers.printf("postprocessing '{}' in serial...\n".format(assignName))

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

			# run the entry
			runEntry(filename, students, helpers, assignment, args, allowPartners)

	# all done
	return True
