import helpers.common as common

# the big kahuna
def run(students, assignments, args, helpers):
	for assignment in assignments:
		# create an empty cluster map for this assignment
		clusters = {}

		# for each file
		files = assignment.args["files"]
		for filename in files:
			# for each pair of students
			for i in range(len(students)):
				for j in range(i):
					student1 = students[i]
					student2 = students[j]
					hashFilename = common.makeFilenameSafe(filename) + "lazy_hash.txt"

					student1Hash = helpers.readFromPreprocessed(student1, assignment.name, hashFilename)
					student2Hash = helpers.readFromPreprocessed(student2, assignment.name, hashFilename)

					if student1Hash != None and student2Hash != None:
						# see if the hashes match
						if student1Hash == student2Hash:
							# if they do, add to the cluster
							member1 = common.Member(student1, assignment.name, helpers)
							member2 = common.Member(student2, assignment.name, helpers)

							# find an existing cluster or create a new one
							cluster = None
							if clusters.has_key(student1Hash):
								cluster = clusters[student1Hash]
							else:
								cluster = common.Cluster(True, filename, 100)
								clusters[student1Hash] = cluster

							# add these students
							cluster.add(member1)
							cluster.add(member2)

		# postprocess the clusters
		clusterArray = []
		for key, cluster in clusters.items():
			clusterArray.append(cluster)

		resultFilename = common.makeFilenameSafe(filename) + "lazy_results.json"
		common.clustersToStandardJSON(clusterArray, assignment.name, resultFilename, helpers)

		# say we're done with this assignment
		helpers.printf("Finised assignment '{}'...\n".format(assignment.name))

	# we did it!
	return True