from index import run as runIndex
import math

def weightFun(key, students, total):
	return 1.0 + (1.0 - float(len(students))/total)

def genKeys(text):
	return text.split("\n")

def run(students, assignments, args, helpers):
	runIndex(students, assignments, args, helpers, weightFun, genKeys)
	return True
