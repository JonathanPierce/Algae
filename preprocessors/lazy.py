import re
from hashlib import sha256
import helpers.common as common

def mangle(text, student, assignment, filename, helpers):
	# convert to uppercase
	text = text.upper()

	# remove most comments
	text = re.sub("\/\/.*\n", "\n", text)
	text = re.sub("\/\*(.|\n)*\*\/", "\n", text)

	# remove certain other characters ( ) ; , { } _ ' "
	# also whitespace
	text = re.sub("\(|\)|;|,|}|{|_|'|\"|\s", "", text)

	# write to preprocessed
	helpers.writeToPreprocessed(text, student, assignment, filename + "lazy_processed.txt")

def run(students, assignments, args, helpers):
	# for each assignment
	for assign in assignments:
		# for each student
		for student in students:
			# for each specificied file
			files = assign.args["files"]
			for filename in files:
				# read the raw text
				rawText = helpers.readFromAssignment(student, assign.name, filename)

				if rawText != None:
					# make a friendly filename for saving
					safeFilename = common.makeFilenameSafe(filename)

					# mangle it, write the mangled text
					mangle(rawText, student, assign.name, safeFilename, helpers)

	# all done
	return True