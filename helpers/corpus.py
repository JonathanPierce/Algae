# valdiates the corpus and provides helper functions to it

import io
import os

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
	