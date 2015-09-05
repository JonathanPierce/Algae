# valdiates the corpus and provides helper functions to it

import io
import os
import csv
import shutil

def splitFilename(path):
	# returns a tuple of (folder_path, filename)
	split = path.split('/')
	return ("/".join(split[:-1]), split[-1])
	
class Corpus:
	def __init__(self, config):
		# keep a reference to the config
		self.config = config
		
		# validate corpus path exists
		if os.path.exists(config.corpusPath) == False:
			io.printErrorAndExit("corpus not found at {}".format(config.corpusPath))
		
		# validate that students.txt exists, create array
		studentText = io.readFile(config.corpusPath + "students.txt")
		self.students = []
		studentText = studentText.strip().split("\n")
		for student in studentText:
			self.students.append(student.strip())

		# try to load the semester map
		self.hasSemesters = False
		self.semesterMap = {}
		if os.path.exists(config.corpusPath + "semesters.csv"):
			handle = open(config.corpusPath + "semesters.csv", "r")
			reader = csv.reader(handle)
			for row in reader:
				self.semesterMap[row[0]] = row[1]
			self.hasSemesters = True

	def getAssignmentPath(self, student, assignment, filename):
		path = self.config.corpusPath + student + '/' + assignment + '/' + filename
		if os.path.exists(path):
			return path
		else:
			return None

	def getPreprocessedPath(self, student, assignment, filename):
		path = self.config.corpusPath + student + '/' + assignment + '/__algae__/' + filename
		if os.path.exists(path):
			return path
		else:
			return None

	def getProcessedPath(self, assignment, filename):
		path = self.config.corpusPath + '__algae__/processed/' + assignment + '/' + filename
		if os.path.exists(path):
			return path
		else:
			return None

	def readFromAssignment(self, student, assignment, filename):
		path = self.config.corpusPath + student + '/' + assignment + '/' + filename
		if os.path.exists(path):
			return io.readFile(path)
		else:
			return None
		
	def readFromPreprocessed(self, student, assignment, filename):
		path = self.config.corpusPath + student + '/' + assignment + '/__algae__/' + filename
		if os.path.exists(path):
			return io.readFile(path)
		else:
			return None
		
	def readFromProcessed(self, assignment, filename):
		path = self.config.corpusPath + '__algae__/processed/' + assignment + '/' + filename
		if os.path.exists(path):
			return io.readFile(path)
		else:
			return None
		
	def readFromPostprocessed(self, assignment, filename):
		path = self.config.corpusPath + '__algae__/postprocessed/' + assignment + '/' + filename
		if os.path.exists(path):
			return io.readFile(path)
		else:
			return None
		
	def writeToPreprocessed(self, text, student, assignment, filename):
		split = splitFilename(filename)
		folderPath = self.config.corpusPath + student + '/' + assignment + '/__algae__/' + split[0]
		if os.path.exists(folderPath) == False:
			os.makedirs(folderPath)
		
		io.writeFile(text, folderPath + '/' + split[1])
		
	def writeToProcessed(self, text, assignment, filename):
		split = splitFilename(filename)
		folderPath = self.config.corpusPath + '/__algae__/processed/' + assignment + '/' + split[0]
		if os.path.exists(folderPath) == False:
			os.makedirs(folderPath)
		
		io.writeFile(text, folderPath + '/' + split[1])
	
	def writeToPostprocessed(self, text, assignment, filename):
		split = splitFilename(filename)
		folderPath = self.config.corpusPath + '/__algae__/postprocessed/' + assignment + '/' + split[0]
		if os.path.exists(folderPath) == False:
			os.makedirs(folderPath)
		
		io.writeFile(text, folderPath + '/' + split[1])

	def getSemester(self, student):
		if self.hasSemesters == False:
			return "unspecified"
		if self.semesterMap.has_key(student):
			return self.semesterMap[student]
		return None

	def cleanPreprocessed(self, student, assignment):
		path = self.config.corpusPath + student + '/' + assignment + '/__algae__'
		if os.path.exists(path):
			shutil.rmtree(path)

	def cleanProcessed(self, assignment):
		path = self.config.corpusPath + '/__algae__/processed/' + assignment
		if os.path.exists(path):
			shutil.rmtree(path)
	
	def cleanPostprocessed(self, assignment):
		path = self.config.corpusPath + '/__algae__/postprocessed/' + assignment
		if os.path.exists(path):
			shutil.rmtree(path)