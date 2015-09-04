# Converts C/C++ files flatly into their tokens
import tokenizer.main as tokenizer
import helpers.common as common
import helpers.io as io

def run(students, assignments, args, helpers):
	# for each assignment
	for assign in assignments:
		helpers.printf("tokenizing '{}'...".format(assign.name))
		index = 0

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

			index = index + 1
			if index % 20 == 0:
				io.printRaw(".")

		print " done!"

	# all done here
	return True