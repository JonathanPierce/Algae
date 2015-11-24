import helpers.common as common
from multiprocessing import Process
import math

class IndexStudent():
	def __init__(self, student):
		self.student = student
		self.count = 1

class IndexEntry():
	def __init__(self):
		self.weight = 0.0
		self.students = []

	def add(self, student):
		entry = self.contains(student)

		if entry != None:
			# increase the count by 1
			entry.count += 1
		else:
			# create an add a new entry
			entry = IndexStudent(student)
			self.students.append(entry)

	def contains(self, student):
		for elem in self.students:
			if elem.student == student:
				return elem

		return None

class InvertedIndex():
	def __init__(self):
		self.index = {}

	def add(self, key, student):
		if key in self.index:
			self.index[key].add(student)
		else:
			entry = IndexEntry()
			entry.add(student)
			self.index[key] = entry

	def prune(self, threshold):
		results = {}

		for key in self.index:
			entry = self.index[key]

			if float(len(entry.students)) < threshold:
				results[key] = entry

		self.index = results

	def weight(self, weightFun, total):
		for key in self.index:
			entry = self.index[key]
			entry.weight = weightFun(key, entry.students, float(total))

	def scoreStudent(self, student, partner, keys):
		results = {}

		# for every unique key
		for key in set(keys):
			if key in self.index:
				entry = self.index[key]

				# find the count for us
				studentCount = 0.0
				for current in entry.students:
					if current.student == student:
						studentCount = float(current.count)

				# add the proper score for this key for each match
				for current in entry.students:
					if current.student != student:
						if current.student in results:
							results[current.student] += entry.weight * math.log(1.0 + min(studentCount, float(current.count)))
						else:
							results[current.student] = entry.weight * math.log(1.0 + min(studentCount, float(current.count)))

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

		for student in students:
			# try to read the file
			safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
			text = helpers.readFromPreprocessed(student, assignName, safeFilename)
			if text != None:
				# generate the keys
				keys = genKeys(text)

				# add to the index
				for key in keys:
					index.add(key, student)

		# prune and weight
		index.prune(threshold)
		index.weight(weightFun, len(students))

		# build the pair results
		results = common.PairResults()

		seen = []
		for student in students:
			# retreive the keys
			safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
			text = helpers.readFromPreprocessed(student, assignName, safeFilename)
			if text != None:
				# generate the keys
				keys = genKeys(text)

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

		# normalize the scores to range 0-100
		biggest = 0.0
		for pair in results.pairs:
			if pair.score > biggest:
				biggest = float(pair.score)

		for pair in results.pairs:
			pair.score = (float(pair.score) / biggest) * 100.0

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
