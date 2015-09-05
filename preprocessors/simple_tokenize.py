# Converts C/C++ files flatly into their tokens
import tokenizer.main as tokenizer
import helpers.common as common
import helpers.io as io
from multiprocessing import Process

def doAssignment(students, assign, helpers):
	helpers.printf("tokenizing '{}' in parellel...\n".format(assign.name))

	# for each student
	for student in students:
		# for each specificied file
		files = assign.args["files"]
		for filename in files:
			path = helpers.getAssignmentPath(student, assign.name, filename)
			if path != None:
				# tokenize the file
				result = tokenizer.simple(path)

				# write the result
				safeFilename = common.makeFilenameSafe(filename) + "tokenized.txt"
				helpers.writeToPreprocessed(result, student, assign.name, safeFilename)

	# all done!
	helpers.printf("Finished '{}'!\n".format(assign.name))

def run(students, assignments, args, helpers):
	# threads to join
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=doAssignment, args=(students, assign, helpers))
		threads.append(t)
		t.start()

	# join then
	for t in threads:
		t.join()

	# all done here
	return True