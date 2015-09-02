#!/usr/bin/env python

import helpers.io as io
from helpers.config import Config
from helpers.progress import Progress
from helpers.args import Args
from helpers.args import getConfigFile
from helpers.corpus import Corpus
from helpers.runner import Runner

if __name__ == "__main__":
	io.printLine()
	print "Welcome to Algae!"
	io.printLine()
	
	# import the config
	io.printRaw('importing configuration... ')
	configFile = getConfigFile()
	config = Config(configFile)
	print "done!"
	
	# import the progress
	io.printRaw('importing progress... ')
	progress = Progress(configFile)
	print "done!"
	
	# check program arguments, generate jobs
	io.printRaw('checking arugments... ')
	args = Args(config)
	print "done!"
	
	# check the corpus
	io.printRaw('checking corpus... ')
	corpus = Corpus(config)
	print "done!"
	io.printLine()
	
	# run the jobs
	print "running jobs:\n"
	runner = Runner(config, progress, args, corpus)
	runner.run()
	
	# all done!
	io.printLine()
	print "Goodbye!"
	io.printLine()
