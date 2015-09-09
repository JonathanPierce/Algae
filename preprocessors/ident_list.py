from tokenizer.tokenizer import Tokenizer
import helpers.common as common
import re

def tokenize(path):
	t = Tokenizer(path)
	tokens = t.raw_tokenize()

	idents = []
	for token in tokens:
		if token.kind.name == "IDENTIFIER":
			name = token.spelling.lower()
			name = re.sub("_", "", name)
			if name not in idents:
				idents.append(name)

	return "\n".join(idents)

def run(students, assignments, args, helpers):
	# for each assignment
	for assign in assignments:
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

	# all done!
	return True