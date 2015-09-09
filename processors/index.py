import helpers.common as common
from multiprocessing import Process

class IndexEntry():
	def __init__(self):
		self.weight = 0.0
		self.students = []

	def add(self, student):
		if student not in self.students:
			self.students.append(student)

class InvertedIndex():
	def __init__(self):
		self.index = {}

	def add(self, key, student):
		if self.index.has_key(key):
			self.index[key].add(student)
		else:
			entry = IndexEntry()
			entry.add(student)
			self.index[key] = entry

	def prune(self, threshold):
		results = {}

		for key in self.index:
			entry = self.index[key]

			if len(entry.students) < threshold:
				results[key] = entry

		self.index = results

	def weight(self, weightFun):
		for key in self.index:
			entry = self.index[key]
			entry.weight = weightFun(key, entry.students)

	def scoreStudent(self, student, partner, keys):
		results = {}

		for key in set(keys):
			if self.index.has_key(key):
				entry = self.index[key]

				for current in entry.students:
					if current != student and current != partner:
						if results.has_key(current):
							results[current] += entry.weight
						else:
							results[current] = entry.weight

		return results

def runAssignment(students, assignment, args, helpers, weightFun, genKeys):
	assignName = assignment.name
	files = assignment.args["files"]
	allowPartners = assignment.args["allowPartners"]
	threshold = args["threshold"] * float(len(students))
	sourceSuffix = args["sourceSuffix"]
	resultsSuffix = args["resultsSuffix"]

	helpers.printf("Running assignment '{}' in parellel...\n".format(assignName))

	for filename in files:
		# build the index
		index = InvertedIndex()
		keysPerStudent = {}

		for student in students:
			# try to read the file
			safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
			text = helpers.readFromPreprocessed(student, assignName, safeFilename)
			if text != None:
				# generate the keys
				keys = genKeys(text)
				keysPerStudent[student] = keys

				# add to the index
				for key in keys:
					index.add(key, student)

		# prune and weight
		index.prune(threshold)
		index.weight(weightFun)

		# build the pair results
		results = common.PairResults()

		seen = []
		for student in students:
			# retreive the keys
			if student in keysPerStudent:
				keys = keysPerStudent[student]

				# get the member (for the partner)
				member = common.Member(student, assignName, helpers)
				partner = member.partner

				# handle allowPartners
				if not allowPartners:
					partner = None

				# get the score results
				studentResults = index.scoreStudent(student, partner, keys)

				# add to pair results
				for other in studentResults:
					if other not in seen:
						pair = common.PairResult(student, other, studentResults[other])
						results.add(pair)

			# prevent duplicates
			seen.append(student)

		# flush to disk
		resultFilename = common.makeFilenameSafe(filename) + resultsSuffix
		common.pairResultsToProcessedJSON(results, assignName, resultFilename, helpers)

	# all done
	helpers.printf("Finished '{}'!\n".format(assignName))

def run(students, assignments, args, helpers, weightFun, genKeys):
	# threads to join later
	threads = []

	# for each assignment
	for assignment in assignments:
		t = Process(target=runAssignment, args=(students, assignment, args, helpers, weightFun, genKeys))
		threads.append(t)
		t.start()

	# wait for all to finis
	for t in threads:
		t.join()

	# all done
	return True