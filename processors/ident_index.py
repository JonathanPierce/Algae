from index import run as runIndex
import math

def weightFun(key, students):
	return (1.0 / float(len(students))) * math.log(float(len(key)) + 1.0)

def genKeys(text):
	return text.split("\n")

def run(students, assignments, args, helpers):
	runIndex(students, assignments, args, helpers, weightFun, genKeys)
	return True