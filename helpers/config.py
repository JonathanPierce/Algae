import io

class Assignment:
	def __init__(self, assignment):
		self.name = assignment['name']
		if assignment.has_key('args'):
			self.args = assignment['args']
		else:
			self.args = None
		
class Preprocessor:
	def __init__(self, preprocessor):
		self.isReference = preprocessor.has_key('job')
		if self.isReference:
			self.job = preprocessor['job']
			self.preprocessor = preprocessor['preprocessor']
		else:
			self.name = preprocessor['name']
			if preprocessor.has_key('args'):
				self.args = preprocessor['args']
			else:
				self.args = None
		
# also for postprocessors
class Processor:
	def __init__(self, processor):
		self.name = processor['name']
		if processor.has_key('args'):
			self.args = processor['args']
		else:
			self.args = None

class Job:
	def __init__(self, job):
		self.name = job['name']
		self.assignments = []
		self.preprocessors = []
		self.processor = None
		self.postprocessors = []
		
		for assignment in job['assignments']:
			self.assignments.append(Assignment(assignment))
			
		for preprocessor in job['preprocessors']:
			self.preprocessors.append(Preprocessor(preprocessor))
			
		self.processor = Processor(job['processor'])
		
		for postprocessor in job['postprocessors']:
			self.postprocessors.append(Processor(postprocessor))
		

# main entry point
class Config:
	def __init__(self):
		try:
			# Read the JSON, set basic attributes
			self.rawJSON = io.readJSON('config.json')
			self.corpusPath = self.rawJSON['corpusPath']
			
			# Process the jobs
			self.jobs = []
			for job in self.rawJSON['jobs']:
				self.jobs.append(Job(job))
		except:
			io.printErrorAndExit("Invalid configuration file.")
