import pygments.lexers.hdl as lexers
from multiprocessing import Process
import helpers.common as common
tokenizer = lexers.VerilogLexer()

def compress_value(value):
	names = ['always', 'always_comb', 'always_ff', 'always_latch', 'and', 'assign', 'automatic', 'begin', 'break', 'buf', 'bufif0', 'bufif1', 'case', 'casex', 'casez', 'cmos', 'const', 'continue', 'deassign', 'default', 'defparam', 'disable', 'do', 'edge', 'else', 'end', 'endcase', 'endfunction', 'endgenerate', 'endmodule', 'endpackage', 'endprimitive','endspecify', 'endtable', 'endtask', 'enum', 'event', 'final', 'for','force', 'forever', 'fork', 'function', 'generate', 'genvar', 'highz0','highz1', 'if', 'initial', 'inout', 'input', 'integer', 'join', 'large','localparam', 'macromodule', 'medium', 'module', 'nand', 'negedge','nmos', 'nor', 'not', 'notif0', 'notif1', 'or', 'output', 'packed','parameter', 'pmos', 'posedge', 'primitive', 'pull0', 'pull1','pulldown', 'pullup', 'rcmos', 'ref', 'release', 'repeat', 'return','rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'signed','small', 'specify', 'specparam', 'strength', 'string', 'strong0','strong1', 'struct', 'table', 'task', 'tran', 'tranif0', 'tranif1','type', 'typedef', 'unsigned', 'var', 'vectored', 'void', 'wait','weak0', 'weak1', 'while', 'xnor', 'xor', 'byte', 'shortint', 'int', 'longint', 'integer', 'time','bit', 'logic', 'reg', 'supply0', 'supply1', 'tri', 'triand','trior', 'tri0', 'tri1', 'trireg', 'uwire', 'wire', 'wand', 'wo','shortreal', 'real', 'realtime']

	value = value.lower()
	if value in names:
		# compress these down to a single letter
		index = names.index(value)
		return chr(48 + index)

	# leave punctuation and operators alone
	return value

def process_token(token):
	kind = str(token[1])
	value = token[2]

	if "Token.Comment" in kind or "Token.Text" in kind:
		# ignore comments
		return ""

	if "Token.Keyword" in kind or "Token.Punctuation" in kind or "Token.Operator" in kind:
		# ignore common tokens to speed edit distance
		return compress_value(value)

	if "Token.Name" in kind:
		return "@"

	if "Token.Literal" in kind or "Token.String" in kind:
		return "#"

	# catch all for all others
	return "?"


def tokenize(text):
	iterable = tokenizer.get_tokens_unprocessed(text)

	result = ""
	for token in iterable:
		result += process_token(token)

	return result

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
				# tokenize the file
				result = tokenize(text)

				# write the result
				safeFilename = common.makeFilenameSafe(sources[0]) + "vted.txt"
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
