import re
from hashlib import sha256
import helpers.common as common

# http://stackoverflow.com/questions/241327/python-snippet-to-remove-c-and-c-comments
def remove_comments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def mangle_text(text):
	# convert to uppercase
	text = text.upper()

	# remove most comments
	text = remove_comments(text)

	# remove certain other characters ( ) ; , { } _ ' "
	# also whitespace
	return re.sub("\(|\)|;|,|}|{|_|'|\"|\s", "", text)

def mangle(text, student, assignment, filename, helpers):
	text = mangle_text(text)

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
