def run(students, assignments, args, helpers):
	helpers.printf("Preprocessor!\n")
	helpers.printf("{} students and {} assignments\n".format(len(students), len(assignments)))
	helpers.printf(args['message'] + '\n')
	
	helpers.printf(helpers.readFromAssignment("student1", "assignment1", "testing.txt"))
	helpers.writeToPreprocessed("text read from preprocessed\n", "student1", "assignment1", "testing.txt")
	helpers.printf(helpers.readFromPreprocessed("student1", "assignment1", "testing.txt"))
	return True