# a collection of useful helper functions for the processors
import re
import io
import csv

# derp.ext -> derp_ext_
def makeFilenameSafe(filename):
	return re.sub("\.", "_", filename) + "_"

def clustersToStandardJSON(clusters, assignment, filename, helpers):
	results = []
	for cluster in clusters:
		if cluster.hasCheating():
			results.append(cluster.toJSON())

	json = io.getJSONString(results, True)
	helpers.writeToPostprocessed(json, assignment, filename)

# only use with a preprocessor or processor
def getPartner(student, assignment, semester, helpers):
	if student != None:
		partnerText = helpers.readFromAssignment(student, assignment, "partners.txt")
		if partnerText != None:
			partnerText = re.sub(",", "\n", partnerText)
			partnerText = re.sub(":", "\n", partnerText)
			partnerArray = partnerText.strip().split("\n")
			for line in partnerArray:
				line = line.strip().split(" ")[0]
				if len(line) > 1 and line != student:
					otherSemester = helpers.getSemester(line)
					if otherSemester != None and otherSemester == semester:
						return line

	return None

# PairResults take up less space on disk than Corpus results.
# If used properly, can rebuild a corpus in RAM from these.
class PairResult:
	def __init__(self, student1, student2, score):
		self.pair = [student1, student2]
		self.score = score

	def toJSON(self):
		result = {}
		result["score"] = self.score
		result["pair"] = self.pair
		return result

class PairResults:
	def __init__(self, assignment, filename, helpers):
		self.filename = helpers.config.corpusPath + '__algae__/processed/' + assignment + '/' + filename
		self.assignment = assignment
		self.end = filename
		self.handle = None

	# write a line to disk
	def add(self, pair):
		if self.handle == None:
			# create a blank file
			helpers.writeToProcessed("", self.assignment, self.end)			

			self.handle = open(self.filename, "w+")

		string = "{},{},{}\n".format(pair.pair[0], pair.pair[1], pair.score)
		self.handle.write(string)

	# closes the handle
	# IF WE'VE CALLED ADD(), CALL THIS BEFORE ITERATE()
	def finish(self):
		if self.handle != None:
			self.handle.close()
			self.handle = None

	# Generator that allows iteration through all results
	def iterate(self):
		handle = open(self.filename, "r")
		line = handle.readline()
		while line != "":
			parts = line.strip().split(",")

			# create the pair result
			pair = PairResult(parts[0], parts[1], float(parts[2]))
			yield pair

			# get the next line
			line = handle.readline()

		# all done
		handle.close()

	# Sends data to JSON. Can use lots of RAM.
	def toJSON(self):
		# return JSON serialiazble form
		results = []
		for pair in self.iterate():
			results.append(pair.toJSON())
		return results


class Member:
	def __init__(self, student, assignment, helpers):
		self.student = student
		self.semester = helpers.getSemester(student)
		self.partner = getPartner(student, assignment, self.semester, helpers)

	def toJSON(self):
		result = {}
		result["student"] = self.student
		result["partner"] = self.partner
		result["semester"] = self.semester
		return result

class Cluster:
	def __init__(self, allowPartners, filename, score):
		self.members = []
		self.allowPartners = allowPartners
		self.file = filename
		self.score = score
		self.allowMistakes = True # allows (a,b),(b,) situations when true

	def add(self, newMember):
		for member in self.members:
			if member.student == newMember.student:
				# don't add more than once
				return
		self.members.append(newMember)

	# Helper function for CS225 code. Ignore.
	def mp7exception(self):
		# if all members come from fa11 or sp12
		# and the file is maze.cpp, then allow partners
		allEarly = True
		for member in self.members:
			if member.semester not in ["fa11", "sp12"]:
				allEarly = False

		return allEarly and self.file == "maze.cpp"

	def hasCheating(self):
		if len(self.members) < 2:
			# can't have cheating without at least two people
			return False

		if len(self.members) == 2 and (self.allowPartners or self.mp7exception()):
			member1 = self.members[0]
			member2 = self.members[1]
			if member1.partner == None or member2.partner == None:
				# check for a mistake
				if self.allowMistakes == True:
					mistake = (member1.partner == None and member2.partner == member1.student) or (member2.partner == None and member1.partner == member2.student)
					return not mistake
					
				# assume both must have a partner
				return True

			# both must list eachother as partners
			return (member1.student == member2.partner and member2.student == member1.partner) == False

		# 3 or more is cheating
		return True

	def toJSON(self):
		# return JSON serialiazble form
		result = {}
		result["allowPartners"] = self.allowPartners
		result["file"] = self.file
		result["score"] = self.score
		result["members"] = []
		for member in self.members:
			result["members"].append(member.toJSON())
		return result

# Groups pair clusters into larger connected components
def groupPairClusters(clusters, top):
	groups = []

	for cluster in clusters:
		studentList = [cluster.members[0].student, cluster.members[1].student]
		if cluster.members[0].partner != None:
			studentList.append(cluster.members[0].partner)
		if cluster.members[1].partner != None:
			studentList.append(cluster.members[1].partner)

		# collect the groups
		foundMatch = False
		for group in groups:
			for member in group.members:
				# look for a matching member
				if member.student in studentList or member.partner in studentList:
					# some shared member, group together
					group.add(cluster.members[0])
					group.add(cluster.members[1])

					# Adjust the score appropriately
					if top == True:
						group.score = max(group.score, cluster.score)
					else:
						group.score = min(group.score, cluster.score)

					# all done here
					foundMatch = True
					break

			# stop looking for groups if we found one
			if foundMatch == True:
				break

		# add the cluster as its own group if need be
		if foundMatch == False:
			groups.append(cluster)

	# all done
	return groups
