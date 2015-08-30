def run(students, assignments, args, helpers):
	helpers.printf("Processor!")
	helpers.printf("{} students and {} assignments".format(len(students), len(assignments)))
	helpers.printf(args['message'] + '\n')
	return True