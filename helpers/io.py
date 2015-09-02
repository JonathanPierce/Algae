# IO functions to help with reading/writing files/JSON and the terminal

import sys
import json
import os

def printLine():
	print ""
	print "========================================================"
	print ""
	
def printIndented(text, indent):
	printRaw((' ' * (4 * indent)) + '- ' + text)
	
def createIndentedPrinter(indent):
	def printFun(text):
		printIndented(text, indent)
		
	return printFun
	
def printRaw(text):
	sys.stdout.write(text)
	sys.stdout.flush()
	
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
		return None
	
def writeFile(text, filename):
	handle = open(filename, 'w+')
	handle.write(text)
	handle.close()
	
def readJSON(filename):
	filetext = readFile(filename)
	if filetext != None:
		return json.loads(filetext)
	else:
		return None
		
def writeJSON(data, filename):
	try:
		text = json.dumps(data)
		writeFile(text, filename)
	except:
		printErrorAndExit('Data is not JSON serializable.')

def getJSONString(data):
	# pretty print!
	return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
