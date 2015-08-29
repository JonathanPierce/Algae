# handles management of the progress.json file

import io

class Progress:
	def __init__(self):
		# attempt to read an existing progress file
		try:
			self.data = io.readJSON("progress.json")
		except:
			self.data = {}
			
	def flushJSON(self):
		io.writeJSON(self.data, "progress.json")
			
	def queryPreprogress(self, job, name):
		if self.data.has_key(job):
			# see if we have a progress entry for this job
			current = self.data[job]
			if current.has_key('preprocessed'):
				# see if we have an entry for preprocessed
				element = current['preprocessed']
				if element.has_key(name):
					# return the result
					return element[name]
						
		# no match found, return False
		return False
		
		
	def queryProgress(self, job):
		if self.data.has_key(job):
			current = self.data[job]
			if current.has_key('processed'):
				return current['processed']
				
		return False
		
	def queryPostprogress(self, job, name):
		if self.data.has_key(job):
			# see if we have a progress entry for this job
			current = self.data[job]
			if current.has_key('postprocessed'):
				# see if we have an entry for postprocessed
				element = current['postprocessed']
				if element.has_key(name):
					# return the result
					return element[name]
						
		# no match found, return False
		return False
		
	def updatePreprogress(self, job, name, complete):
		if self.data.has_key(job) == False:
			self.data[job] = {}
			
		jobData = self.data[job]
		
		if jobData.has_key('preprocessed') == False:
			jobData['preprocessed'] = {}
			
		preData = jobData['preprocessed']
		preData[name] = complete
		
		# flush the json
		self.flushJSON()
			
		
	def updateProgress(self, job, complete):
		if self.data.has_key(job) == False:
			self.data[job] = {}
			
		jobData = self.data[job]
		jobData['processed'] = complete
			
		# flush JSON
		self.flushJSON()
		
	def updatePostprogress(self, job, name, complete):
		if self.data.has_key(job) == False:
			self.data[job] = {}
			
		jobData = self.data[job]
		
		if jobData.has_key('postprocessed') == False:
			jobData['postprocessed'] = {}
			
		postData = jobData['postprocessed']
		postData[name] = complete
				
		# flush the json
		self.flushJSON()