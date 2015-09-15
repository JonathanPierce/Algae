# removes files identical to what was handled out from the corpus
# preprocessor args:
# - sourceStudent (string): Student (which doesn't have to be in students.txt) containing all blank files.
# assignment args:
# - files (string array): Files to compare ot the blank.

import os
from lazy import mangle_text

def run(students, assignments, args, helpers):
	sourceStudent = args["sourceStudent"]

	for assignment in assignments:
		files = assignment.args["files"]
		for student in students:
			for filename in files:
				# try to get from the sourceStudent
				source = helpers.readFromAssignment(sourceStudent, assignment.name, filename)
				if source != None:
					# try to get from this student
					source = mangle_text(source)
					other = helpers.readFromAssignment(student, assignment.name, filename)
					if other != None:
						other = mangle_text(other)
						# if they are the same, remove
						if source == other:
							path = helpers.getAssignmentPath(student, assignment.name, filename)
							os.system("rm {}".format(path))

	return True
