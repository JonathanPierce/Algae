from index import run as runIndex
from math import log

def weightFun(key, students, total):
	return 1.0 + (1.0 - float(len(students))/total)

def genKeys(text):
	results = []
	tokenLen = 12

	for i in range(0, len(text) - tokenLen):
		results.append(text[i:(i + tokenLen)])

	return results

def run(students, assignments, args, helpers):
	runIndex(students, assignments, args, helpers, weightFun, genKeys)
	return True
