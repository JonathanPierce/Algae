from tokenizer.tokenizer import Tokenizer
import helpers.common as common
from multiprocessing import Process
import re

def tokenize(path):
	t = Tokenizer(path)
	tokens = t.raw_tokenize()

	idents = []
	for token in tokens:
		if token.kind.name == "IDENTIFIER":
			name = token.spelling.lower()
			name = re.sub("_", "", name)
			idents.append(name)

	return "\n".join(idents)

def runFile(students, assign, helpers):
	helpers.printf("Processing assignment '{}' in parellel...\n".format(assign.name))

	# for each student
	for student in students:
		# for each specificied file
		files = assign.args["files"]
		for filename in files:
			# get the path
			path = helpers.getAssignmentPath(student, assign.name, filename)

			if path != None:
				# get the identifiers
				text = tokenize(path)

				# write to a file
				safeFilename = common.makeFilenameSafe(filename) + "identifiers.txt"
				helpers.writeToPreprocessed(text, student, assign.name, safeFilename)

	# all done
	helpers.printf("Finished '{}'!\n".format(assign.name))


def run(students, assignments, args, helpers):
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=runFile, args=(students, assign, helpers))
		threads.append(t)
		t.start()

	# wait for all to finish
	for t in threads:
		t.join()

	# all done!
	return True
