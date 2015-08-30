def run(students, assignments, args, helpers):
	helpers.printf("Postprocessor!\n")
	helpers.printf("{} students and {} assignments\n".format(len(students), len(assignments)))
	helpers.printf(args['message'] + '\n')
	
	helpers.printf(helpers.readFromProcessed("assignment1", "testing.txt"))
	helpers.writeToPostprocessed("text read from postprocessed\n", "assignment1", "testing.txt")
	helpers.printf(helpers.readFromPostprocessed("assignment1", "testing.txt"))
	return True