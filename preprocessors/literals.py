# collects comments, strings, numbers, and other literals
from tokenizer.tokenizer import Tokenizer
import helpers.common as common
from multiprocessing import Process
from hashlib import sha256
from lazy import mangle_text
import clang.cindex
import re

def tokenize(path):
    t = Tokenizer(path)
    tokens = t.raw_tokenize()

    items = []
    for token in tokens:
        if token.kind.name == "LITERAL":
            text = token.spelling
            cursor_kind = clang.cindex.CursorKind
            kind = token.cursor.kind

            if kind == cursor_kind.STRING_LITERAL:
                # do extra processing on strings
                text = sha256(mangle_text(token.spelling)).hexdigest()[:10]

            items.append(text)

        if token.kind.name == "COMMENT":
            hashed = sha256(mangle_text(token.spelling[2:])).hexdigest()[:10]
            items.append(hashed)

    return "\n".join(items)

def runFile(students, assign, helpers):
    helpers.printf("Processing assignment '{}' in parellel...\n".format(assign.name))

    # for each student
    for student in students:
        # for each specificied file
        files = assign.args["files"]
        for filename in files:
            # get the path
            path = helpers.getAssignmentPath(student, assign.name, filename)

            if path != None:
                # get the identifiers
                text = tokenize(path)

                # write to a file
                safeFilename = common.makeFilenameSafe(filename) + "literals.txt"
                helpers.writeToPreprocessed(text, student, assign.name, safeFilename)

    # all done
    helpers.printf("Finished '{}'!\n".format(assign.name))


def run(students, assignments, args, helpers):
    threads = []

    # for each assignment
    for assign in assignments:
        t = Process(target=runFile, args=(students, assign, helpers))
        threads.append(t)
        t.start()

    # wait for all to finish
    for t in threads:
        t.join()

    # all done!
    return True
