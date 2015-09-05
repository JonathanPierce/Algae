# preprocesses files for modified token edit distance (MTED)
# assignment args:
# - entries (array):
# -- entryPoint (string): File that Clang should "compile". If using C++ templates, this may be an instructor-provided main file.
# -- sources (string array): The files that have functions that we are interested in. First file listed should be the primary.
# processor args:
# - compress (bool - optional): Whether the token should be compressed. Defaults to true.

import tokenizer.main as tokenizer
import helpers.common as common
import helpers.io as io
from multiprocessing import Process

def doAssignment(students, assign, helpers, compress):
	helpers.printf("processing '{}' in parellel...\n".format(assign.name))

	# for each student
	for student in students:
		# for each entry
		entries = assign.args["entries"]
		for entry in entries:
			entryPoint = entry["entryPoint"]
			path = helpers.getAssignmentPath(student, assign.name, entryPoint)
			sources = entry["sources"]

			if path != None:
				# tokenize the file
				result = tokenizer.mted(path, sources, compress)

				# write the result
				safeFilename = common.makeFilenameSafe(entryPoint) + "mted.txt"
				helpers.writeToPreprocessed(result, student, assign.name, safeFilename)

	# all done
	helpers.printf("Finished '{}'!\n".format(assign.name))

def run(students, assignments, args, helpers):
	# Compress tokens by default
	compress = True
	if args.has_key("compress"):
		compress = args["compress"]

	# threads to join later
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=doAssignment, args=(students, assign, helpers, compress))
		threads.append(t)
		t.start()

	# join the threads
	for t in threads:
		t.join()

	# all done here
	return True