import helpers.common as common
from multiprocessing import Process
import helpers.io as io
import math

statTypes = ["numLines", "numWhitespace", "numComments", "avgIdentLength", "numFunctions", "numDefines", "numMathOps"]

# finds the mean of the data
def getMean(data, key):
	total = 0.0
	count = 0.0

	for element in data:
		total = total + float(element[key])
		count = count + 1.0

	return total / count

# finds the std. deviation of the data
def getDeviation(data, mean, key):
	totalDiff = 0.0
	count = 0.0

	for element in data:
		totalDiff = totalDiff + (float(element[key]) - mean)**2.0
		count = count + 1.0

	normalized = totalDiff / count
	
	return math.sqrt(normalized)

# gets the z-score of a data point
def zScore(score, mean, deviation):
	return (score - mean) / deviation

class Stat():
	def __init__(self, mean, deviation):
		self.mean = mean
		self.deviation = deviation

def getStats(students, assign, filename, helpers):
	# gather students stats into an array
	studentDict = {}
	array = []

	for student in students:
		safeFilename = common.makeFilenameSafe(filename) + "stats.json"
		path = helpers.getPreprocessedPath(student, assign.name, safeFilename)
		if path != None:
			json = io.readJSON(path)
			studentDict[student] = json
			array.append(json)

	return (studentDict, array)

def runAssignment(students, assign, args, helpers):
	helpers.printf("Processing assignment '{}' in parellel...\n".format(assign.name))

	threshold = args["threshold"]

	# clusters for this assignment
	clusters = []

	# for each specificied file
	files = assign.args["files"]
	for filename in files:
		# get stats from JSON
		(studentDict, array) = getStats(students, assign, filename, helpers)

		# calculate the stats from all students
		stats = {}
		for stat in statTypes:
			mean = getMean(array, stat)
			deviation = getDeviation(array, mean, stat)
			stats[stat] = Stat(mean, deviation)

		# collect the sum of z-scores for each student
		for student in students:
			if student in studentDict:
				data = studentDict[student]
				total = 0.0
				for stat in statTypes:
					total += abs(zScore(data[stat], stats[stat].mean, stats[stat].deviation))

				if total >= threshold:
					cluster = common.Cluster(False, filename, total)
					member = common.Member(student, assign.name, helpers)
					cluster.add(member)
					clusters.append(cluster)

	# save the clusters
	results = []
	for cluster in clusters:
		results.append(cluster.toJSON())
	json = io.getJSONString(results, True)
	helpers.writeToPostprocessed(json, assign.name, "obfuscation_results.json")
 
	# all done
	helpers.printf("Finished '{}'!\n".format(assign.name))


def run(students, assignments, args, helpers):
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=runAssignment, args=(students, assign, args, helpers))
		threads.append(t)
		t.start()

	# wait for all to finish
	for t in threads:
		t.join()
		
	# all done!
	return True