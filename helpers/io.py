# IO functions to help with reading/writing files/JSON and the terminal

import sys
import json
import os

def printLine():
	print ""
	print "========================================================"
	print ""
	
def printIndented(text, indent):
	print ('\t' * indent) + text
	
def printRaw(text):
	sys.stdout.write(text)
	
def printErrorAndExit(text):
	printLine()
	print 'ERROR: ' + text
	exit(1)
	
def readFile(filename):
	if os.path.exists(filename):
		handle = open(filename, 'r')
		text = handle.read()
		handle.close()
		return text
	else:
		printErrorAndExit('File {} not found.'.format(filename))
	
def writeFile(text, filename):
	handle = open(filename, 'w+')
	handle.write(text)
	handle.close()
	
def readJSON(filename):
	filetext = readFile(filename)
	return json.loads(filetext)
		
def writeJSON(data, filename):
	try:
		text = json.dumps(data)
		writeFile(text, filename)
	except:
		printErrorAndExit('Data is not JSON serializable.')
