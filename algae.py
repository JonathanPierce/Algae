import helpers.io as io
from helpers.config import Config

if __name__ == "__main__":
	io.printLine()
	print "Welcome to Algae!"
	io.printLine()
	
	# import the config
	io.printRaw('importing configuration... ')
	config = Config()
	print "done!"
	
	# import the progress
	io.printRaw('importing progress... ')
	print "done!"
	
	# check program arguments, generate jobs
	io.printRaw('checking arugments... ')
	print "done!"
	
	# check the corpus
	io.printRaw('checking corpus... ')
	print "done!"
	io.printLine()
	
	# run the jobs
	print "running jobs:\n"
	
	# all done!
	io.printLine()
	print "Goodbye!"
	io.printLine()
