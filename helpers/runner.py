# runs the (pre/post)processors, handles progress, etc...

import io
import importlib

def getJobFromConfig(config, jobName):
	for job in config.jobs:
		if job.name == jobName:
			return job
	return None

def getPreprocessorReference(config, job, name):
	job = getJobFromConfig(config, job)
	for pre in job.preprocessors:
		if pre.name == name:
			return pre
	return None
	
class PreprocessorHelpers:
	def __init__(self, corpus):
		self.readFromAssignment = corpus.readFromAssignment
		self.readFromPreprocessed = corpus.readFromPreprocessed
		self.writeToPreprocessed = corpus.writeToPreprocessed
		self.printf = io.createIndentedPrinter(2)
		
class ProcessorHelpers:
	def __init__(self, corpus):
		self.readFromAssignment = corpus.readFromAssignment
		self.readFromPreprocessed = corpus.readFromPreprocessed
		self.writeToProcessed = corpus.writeToProcessed
		self.printf = io.createIndentedPrinter(2)
		
class PostprocessorHelpers:
	def __init__(self, corpus):
		self.readFromProcessed = corpus.readFromProcessed
		self.readFromPostprocessed = corpus.readFromPostprocessed
		self.writeToPostprocessed = corpus.writeToPostprocessed
		self.printf = io.createIndentedPrinter(2)

class Runner:
	def __init__(self, config, progress, args, corpus):
		# keep references
		self.config = config
		self.progress = progress
		self.args = args
		self.corpus = corpus
		
	def run(self):
		args = self.args
		config = self.config
		
		# for each job from args
		for jobName in args.jobs:
			# extract the job from the config
			job = getJobFromConfig(config, jobName)
			
			# print that we are running this job
			print "Running job '{}'...".format(job.name)
			
			# run each specified stage
			success = True
			
			if args.mode == "all" or args.mode == "preprocess":
				success = success and self.runPreprocess(job)
				
			if args.mode == "all" or args.mode == "process":
				success = success and self.runProcess(job)
				
			if args.mode == "all" or args.mode == "postprocess":
				success = success and self.runPostprocess(job)
				
			if success:
				print 'Job completed successfully!\n'
			else:
				print "Job failed. :(\n"
			
		# run each stage from args (checking/updating progress)
		return None
		
	def shouldPreprocess(self, job, name, isReference):
		if "force" in self.args.options and not isReference:
			return True
		return self.progress.queryPreprogress(job, name) == False
		
	def shouldProcess(self, job):
		if "force" in self.args.options:
			return True
		return self.progress.queryProgress(job) == False
		
	def shouldPostprocess(self, job, name):
		if "force" in self.args.options:
			return True
		return self.progress.queryPostprogress(job, name) == False
		
	def runPreprocess(self, job):
		success = True
	
		# for each preprocessor
		for pre in job.preprocessors:
			# print the name
			io.printIndented("running preprocessor '{}'...".format(pre.name), 1)
			
			# if we are a reference, get what we are referencing to
			jobName = job.name
			isReference = pre.isReference
			if pre.isReference:
				jobName = pre.job
				pre = getPreprocessorReference(self.config, pre.job, pre.name)
			
			# see if it has already ran
			if self.shouldPreprocess(jobName, pre.name, isReference):
				# we need to run, first gather arguments
				students = self.corpus.students
				assignments = job.assignments
				args = pre.args
				helpers = PreprocessorHelpers(self.corpus)
				
				# try to import the correct module
				try:
					module = importlib.import_module('preprocessors.' + pre.name)
					
					# run it
					print ""
					success = module.run(students, assignments, args, helpers)
					
					# update progress
					self.progress.updatePreprogress(job.name, pre.name, success)
				except:
					io.printIndented("module '{}' not found or encountered an error.\n".format(pre.name), 1)
					success = False
					
				if success:
					io.printIndented('complete!\n', 1)
				else:
					# fail out
					break
			else:
				# don't need to run
				io.printRaw(' already done!\n')
		
		# return true iff all were sucessful
		return success
		
	def runProcess(self, job):
		success = True
		processor = job.processor
		
		# print the name
		io.printIndented("running processor '{}'...".format(processor.name), 1)
		
		# see if it has already ran
		if self.shouldProcess(job.name):
			# we need to run, first gather arguments
			students = self.corpus.students
			assignments = job.assignments
			args = processor.args
			helpers = ProcessorHelpers(self.corpus)
			
			# try to import the correct module
			try:
				module = importlib.import_module('processors.' + processor.name)
				
				# run it
				print ""
				success = module.run(students, assignments, args, helpers)
				
				# update progress
				self.progress.updateProgress(job.name, success)
			except:
				io.printIndented("module '{}' not found or encountered an error.\n".format(processor.name), 1)
				success = False
				
			if success:
				io.printIndented('complete!\n', 1)
		else:
			# don't need to run
			io.printRaw(' already done!\n')
		
		return success
		
	def runPostprocess(self, job):
		success = True
	
		# for each preprocessor
		for post in job.postprocessors:
			# print the name
			io.printIndented("running postprocessor '{}'...".format(post.name), 1)
			
			# see if it has already ran
			if self.shouldPostprocess(job.name, post.name):
				# we need to run, first gather arguments
				students = self.corpus.students
				assignments = job.assignments
				args = post.args
				helpers = PostprocessorHelpers(self.corpus)
				
				# try to import the correct module
				try:
					module = importlib.import_module('postprocessors.' + post.name)
					
					# run it
					print ""
					success = module.run(students, assignments, args, helpers)
					
					# update progress
					self.progress.updatePostprogress(job.name, post.name, success)
				except:
					io.printIndented("module '{}' not found or encountered an error.\n".format(post.name), 1)
					success = False
					
				if success:
					io.printIndented('complete!\n', 1)
				else:
					# fail out
					break
			else:
				# don't need to run
				io.printRaw(' already done!\n')
		
		# return true iff all were sucessful
		return success