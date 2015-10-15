# Preprocessor for MIPS assignments
from multiprocessing import Process
import helpers.common as common
import re

def processToken(token):
    # are we a directive
    directives = [".data", ".text", ".kdata", ".ktext", ".set", ".ascii", ".asciiz", ".byte", ".halfword", ".word", ".space", ".align", ".double", ".extern", ".float", ".globl", ".half", "eret"]
    if token in directives:
        return "!"

    # are we an instruction
    instructions = ["add", "addu", "addi", "addiu", "and", "andi", "div", "divu", "mult", "multu", "nor", "or", "ori", "sll", "sllv", "sra", "srav", "srl", "srlv", "sub", "subu", "xor", "xori", "lhi", "llo", "slt", "sltu", "slti", "sltiu", "beq", "bgtz", "blez", "bne", "j", "jal", "jalr", "jr", "lb", "lbu", "lh", "lhu", "lw", "sb", "sh", "sw", "mfhi", "mflo", "mthi", "mtlo", "trap", "mul", "lui", "syscall", "abs", "rem", "move", "clear", "not", "li", "la", "bgt", "blt", "bge", "ble", "break", "daddi", "bal", "bgtu", "bltu", "bgeu", "bleu"]

    if token in instructions:
        if token in ["andi", "divu", "multu", "ori", "subu", "addu", "addi", "xori"]:
            token = token[:-1]
        
        return chr(ord("(") + instructions.index(token))

    # are we a register
    isNumRegister = re.match("^\$[0-3][0-9]?$", token) != None
    isNamedRegister = re.match("^\$[vatsk][0-9]$", token) != None
    isSpecialRegister = token in ["$zero", "$lo", "$hi", "$at", "$gp", "$sp", "$fp", "$ra"]
    if isNumRegister or isNamedRegister or isSpecialRegister:
        return "$"

    # are we a number/hex/char/string/literal
    isNumber = re.match("^(-?)[0-9]+(\.[0-9]*)?$", token) != None
    isHex = re.match("^0x[0-9a-f]+$", token) != None
    isChar = re.match("^'.'$", token) != None
    isString = re.match("^\".*\"$", token) != None
    if isNumber or isChar or isString or isHex:
        return "#"

    # are we a label declaration
    if re.match("^[_a-z][_a-z0-9\.]*(:|=)$",token) != None:
        return "%"

    # are we a label use
    if re.match("^[_a-z][_a-z0-9\.]*$", token) != None:
        return "&"

    # WTF
    # print "No match for token {}".format(token)
    return '?'

def processTokens(tokens):
    result = ""

    for token in tokens:
        result += processToken(token.strip())

    return result

def processMIPS(text):
    # convert to lowercase, remove comments:
    text = text.lower()
    text = re.sub("#.*\n", "\n", text)

    # handle spacing around ":"
    text = re.sub("\s:", ":", text)
    text = re.sub(":", ": ", text)

    # replace certain punctuation with spaces
    text = re.sub(",|\(|\)|;"," ", text)

    # reduce long whitespace to a single space
    text = re.sub("\s+", " ", text)

    # get each token
    return processTokens(text.strip().split(" "))

def doAssignment(students, assign, helpers):
	helpers.printf("processing '{}' in parellel...\n".format(assign.name))

	# for each student
	for student in students:
		# for each entry
		entries = assign.args["entries"]
		for entry in entries:
			sources = entry["sources"]

			# try to read the text
			text = helpers.readFromAssignment(student, assign.name, sources[0])

			if text != None:
				# process the file
				result = processMIPS(text)

				# write the result
				safeFilename = common.makeFilenameSafe(sources[0]) + "mips.txt"
				helpers.writeToPreprocessed(result, student, assign.name, safeFilename)

	# all done
	helpers.printf("Finished '{}'!\n".format(assign.name))

def run(students, assignments, args, helpers):
	# threads to join later
	threads = []

	# for each assignment
	for assign in assignments:
		t = Process(target=doAssignment, args=(students, assign, helpers))
		threads.append(t)
		t.start()

	# join the threads
	for t in threads:
		t.join()

	# all done here
	return True
