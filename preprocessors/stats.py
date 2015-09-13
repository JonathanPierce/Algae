from tokenizer.tokenizer import Tokenizer
import helpers.common as common
from multiprocessing import Process
import helpers.io as io
import re

def genStats(path, helpers):
	t = Tokenizer(path)
	tokens = t.raw_tokenize()

	# stats
	numLines = 0
	numWhitespace = 0
	numComments = 0
	avgIdentLength = 0
	numFunctions = 0 # ident followed by (, declarations and calls
	numDefines = 0
	numMathOps = 0
	lenLongestLine = 0
	numReturns = 0

	# other data
	idents = []
	text = io.readFile(path)
	lastWasIdent = False

	# get info from tokens
	for token in tokens:
		# look for a comment
		if token.kind.name == "COMMENT":
			numComments += 1

		# look for math ops
		if token.spelling in ["+", "-", "*", "/", "|", "&", "+=", "-=", "*=", "/=", ">>=", "<<=", "++", "--", "~", ">>"]:
			numMathOps += 1

		# look for function decs/calls
		if lastWasIdent and token.spelling == "(":
			numFunctions += 1

		# count the number of returns
		if token.spelling == "return":
			numReturns += 1

		# add the identifier to the list, set lastWasIdent
		if token.kind.name == "IDENTIFIER":
			idents.append(token.spelling)
			lastWasIdent = True
		else:
			lastWasIdent = False

	# get average ident length
	total = 0.0
	for ident in idents:
		total += float(len(ident))
	avgIdentLength = total / float(len(idents))

	# find the number of defines
	defines = re.findall("#define ", text.lower())
	numDefines = len(defines)

	# find the number of lines
	lines = text.split("\n")
	numLines = len(lines)

	# get the length of the longest line
	for line in lines:
		if len(line) > lenLongestLine:
			lenLongestLine = len(line)

	# find the total amount of whitespace
	for char in text:
		if char in [" ", "\n", "\t"]:
			numWhitespace += 1

	# create a dict of results and return
	results = {}
	results["numLines"] = numLines
	results["numWhitespace"] = numWhitespace
	results["numComments"] = numComments
	results["avgIdentLength"] = avgIdentLength
	results["numFunctions"] = numFunctions
	results["numDefines"] = numDefines
	results["numMathOps"] = numMathOps
	results["numReturns"] = numReturns
	results["lenLongestLine"] = lenLongestLine
	return results

def runAssignment(students, assign, helpers):
	helpers.printf("Processing assignment '{}' in parellel...\n".format(assign.name))

	# for each student
	for student in students:
		# for each specificied file
		files = assign.args["files"]
		for filename in files:
			# get the path
			path = helpers.getAssignmentPath(student, assign.name, filename)

			if path != None:
				# get the stats
				stats = genStats(path, helpers)

				# write to a file
				safeFilename = common.makeFilenameSafe(filename) + "stats.json"
				text = io.getJSONString(stats, True)
				helpers.writeToPreprocessed(text, student, assign.name, safeFilename)

	# all done
	helpers.printf("Finished '{}'!\n".format(assign.name))


def run(students, assignments, args, helpers):
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=runAssignment, args=(students, assign, helpers))
		threads.append(t)
		t.start()

	# wait for all to finish
	for t in threads:
		t.join()
		
	# all done!
	return True
	