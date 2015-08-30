import helpers.io as io
from helpers.config import Config
from helpers.progress import Progress
from helpers.args import Args
from helpers.corpus import Corpus

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
	progress = Progress()
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
	
	# all done!
	io.printLine()
	print "Goodbye!"
	io.printLine()
