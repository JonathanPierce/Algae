# Filters standard-format results down to those containing students from a specific semester
# assignment args:
# - filterFiles (string array - optional): Postprocessed filenames to try to read if singleFile is off.
# postprocessor args:
# - semester (string): The semester we are looking for.
# - singleFile (bool - optional - defaults to false): Results contained in a single file.
# - inputFile (string - optional) - input file to use in singleFile is true

import helpers.io as io
import helpers.common as common

def filterData(filename, assignment, args, helpers):
	jsonpath = helpers.getPostprocessedPath(assignment.name, filename)
	if jsonpath != None:
		json = io.readJSON(jsonpath)
		if json != None:
			# search the members for students from the given semester
			results = []
			semester = args["semester"]

			for element in json:
				hasSemester = False
				for mem in element['members']:
					if mem['semester'] == semester:
						hasSemester = True

				if hasSemester == True:
					results.append(element)

			# write back to disk
			resultJSON = io.getJSONString(results, True)
			helpers.writeToPostprocessed(resultJSON, assignment.name, semester + "_" + filename)	

def run(students, assignments, args, helpers):
	singleFile = False
	if args.has_key("singleFile") and args["singleFile"] == True:
		singleFile = True

	# for each assignment
	for assignment in assignments:
		# for each postprocessed file in the config
		if singleFile == False:
			for filename in assignment.args['filterFiles']:
				# filter this assignment
				filterData(filename, assignment, args, helpers)
		else:
			filterData(args['inputFile'], assignment, args, helpers)
			
	# all done
	return True