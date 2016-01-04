import helpers.common as common
from multiprocessing import Process
import math
from index import *
from token_index import weightFun as tokenWeightFun
from  token_index import genKeys as tokenGenKeys
from ident_index import weightFun as identWeightFun
from ident_index import genKeys as identGenKeys

def runAssignment(students, assignment, args, helpers, weightFun, genKeys):
    assignName = assignment.name
    files = assignment.args["files"]
    allowPartners = assignment.args["allowPartners"]
    threshold = args["threshold"] * float(len(students))
    sourceSuffixes = ["tokenized.txt", "identifiers.txt", "literals.txt"]
    resultsSuffix = args["resultsSuffix"]

    helpers.printf("Running assignment '{}' in parellel...\n".format(assignName))

    for filename in files:
        indexes = [InvertedIndex(), InvertedIndex(), InvertedIndex()]

        # for each type of Data
        for i in range(3):
            sourceSuffix = sourceSuffixes[i]
            curWeightFun = weightFun[i]
            curGenKeys = genKeys[i]
            index = indexes[i]

            for student in students:
                # try to read the file
                safeFilename = common.makeFilenameSafe(filename) + sourceSuffix
                text = helpers.readFromPreprocessed(student, assignName, safeFilename)
                if text != None:
                    # generate the keys
                    keys = curGenKeys(text)

                    # add to the index
                    for key in keys:
                        index.add(key, student)

            # prune and weight
            index.prune(threshold)
            index.weight(curWeightFun, len(students))

        # build the denormalized pair results
        resultFilename = common.makeFilenameSafe(filename) + "raw_" + resultsSuffix
        results = common.PairResults(assignName, resultFilename, helpers)

        seen = []
        for student in students:
            combined = {}

            for i in range(3):
                # retreive the keys
                safeFilename = common.makeFilenameSafe(filename) + sourceSuffixes[i]
                text = helpers.readFromPreprocessed(student, assignName, safeFilename)
                index = indexes[i]

                if text != None:
                    # generate the keys
                    keys = genKeys[i](text)

                    # get the member (for the partner)
                    member = common.Member(student, assignName, helpers)
                    partner = member.partner

                    # handle allowPartners
                    if not allowPartners:
                        partner = None

                    # get the score results
                    studentResults = index.scoreStudent(student, partner, keys)

                    # add to results
                    for other in studentResults:
                        if other in combined:
                            # add the score
                            combined[other] += studentResults[other]
                        else:
                            # create the entry
                            combined[other] = studentResults[other]

            # add to pair results
            for other in combined:
                if other not in seen:
                    pair = common.PairResult(student, other, combined[other])
                    results.add(pair)

            # prevent duplicates
            seen.append(student)

        # normalize the scores to range 0-100
        results.finish()

        biggest = 0.0
        for pair in results.iterate():
            if pair.score > biggest:
                biggest = float(pair.score)

        # flush to disk
        finalResultFilename = common.makeFilenameSafe(filename) + resultsSuffix
        finalResults = common.PairResults(assignName, finalResultFilename, helpers)

        for pair in results.iterate():
            pair.score = (float(pair.score) / biggest) * 100.0
            finalResults.add(pair)

        finalResults.finish()

    # all done
    helpers.printf("Finished '{}'!\n".format(assignName))

def run(students, assignments, args, helpers):
    # threads to join later
    threads = []

    def literalWeightFun(key, students, total):
        return 1.0 + ((1.0 - float(len(students))/total) * 5.0)

    # for each assignment
    for assignment in assignments:
        weightFun = [tokenWeightFun, identWeightFun, literalWeightFun]
        genKeys = [tokenGenKeys, identGenKeys, identGenKeys]

        t = Process(target=runAssignment, args=(students, assignment, args, helpers, weightFun, genKeys))
        threads.append(t)
        t.start()

    # wait for all to finish
    for t in threads:
        t.join()

    # all done
    return True
