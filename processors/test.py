def run(students, assignments, args, helpers):
	helpers.printf("Processor!\n")
	helpers.printf("{} students and {} assignments\n".format(len(students), len(assignments)))
	helpers.printf(args['message'] + '\n')
	
	helpers.printf(helpers.readFromAssignment("student1", "assignment1", "testing.txt"))
	helpers.printf(helpers.readFromPreprocessed("student1", "assignment1", "testing.txt"))
	helpers.writeToProcessed("text read from processed\n", "assignment1", "testing.txt")
	return True