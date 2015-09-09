from index import run as runIndex

def weightFun(key, students):
	return 1.0 / float(len(students))

def genKeys(text):
	results = []
	tokenLen = 15

	for i in range(0, len(text) - tokenLen):
		results.append(text[i:(i + tokenLen)])

	return results

def run(students, assignments, args, helpers):
	runIndex(students, assignments, args, helpers, weightFun, genKeys)
	return True