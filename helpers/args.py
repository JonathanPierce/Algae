# interprets program args correctly
import sys
import io

class Args:
	def __init__(self, config):
		self.mode = "all"
		self.jobs = []
		self.options = []
		
		args = sys.argv[1:]
		
		if len(args) > 0:
			# check if the first arg is a mode
			if args[0].lower() in ["all", 'preprocess', 'postprocess', 'process']:
				self.mode = args[0].lower()
				args = args[1:]
				
			# process jobs and options
			while len(args) > 0:
				arg = args[0]
				args = args[1:]
				
				found = False
				for job in config.jobs:
					# case sensitive
					if job.name == arg:
						self.jobs.append(arg)
						found = True
						break
						
				if found == False and arg.lower() in ["--force"]:
					self.options.append(arg[2:].lower())
					found = True
					
				if found == False:
					# job not found or option invalid
					io.printErrorAndExit('Invalid job name or option specified as argument.')
					
		# no jobs? Add them all.
		if len(self.jobs) == 0:
			for job in config.jobs:
				self.jobs.append(job.name)
		
		# Mode not 'all'? Add force.
		if self.mode != 'all' and 'force' not in self.options:
			self.options.append('force')
