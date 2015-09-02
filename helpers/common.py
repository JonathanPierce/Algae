# a collection of useful helper functions for the processors
import re

# derp.ext -> derp_ext_
def makeFilenameSafe(filename):
	return re.sub("\.", "_", filename) + "_"