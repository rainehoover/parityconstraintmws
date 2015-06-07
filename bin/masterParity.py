import subprocess
import sys
import os
from collections import defaultdict

def main():
#	outfile =  # where to write the clauses to (e.g. "out.txt")
	n = int(sys.argv[1]) # number variables
	k = int(sys.argv[2]) # number variables per clause
	m = int(sys.argv[3]) # number of clauses to produce
	i = int(sys.argv[4]) # number of A's
	print("Hello, we'll be doing this " + str(i) + " times!")
	mln = sys.argv[5]
	resultWtBaseStr = sys.argv[6]
	traindb = sys.argv[7]
	query = sys.argv[8]
	testdb = sys.argv[9]
	resultMargBaseStr = sys.argv[10]
	margProbs = defaultdict(float)
	for j in range(i):
		makeClausesCommand = "python ./makeclauses.py " + str(n) + " " + str(k) + " " +str(m) + " " + str(j) 
		print(makeClausesCommand)
#		os.system(makeClausesCommand)
		print("Made one A!")
		# now clauses.text holds clauses for this particular A
		getWeightsCommand = "./learnwts -d -i " + mln + " -o " + resultWtBaseStr + str(j) + " -t " + traindb + " -ne " + query
		print(getWeightsCommand)
		#os.system(getWeightsCommand)
		# now the weights are present learned from this particular parity constraint
		computeMargForGPs(resultWtBaseStr + str(j), resultMargBaseStr, testdb, margProbs)
		print margProbs
	#Now that we have results from all As, divide marg probs by number of A's to get average
	margProbs.update({k: v/i for k, v in margProbs.items()})	
	print margProbs
	finalOutput = open(resultMargBaseStr + "final", "w")
	for k, v in margProbs.items():
		finalOutput.write(k + " " + str(v) + "\n")

def getMargProb(mln, result, test, query, gpredicate):
	inferCommand = "../../../alchemy-2/bin/infer -ms -i " + mln + " -r " + result + " -e " + test + " -q " + query
	print(inferCommand)
	os.system(inferCommand)
	grepCommand = "grep '" + gpredicate + "' " + result
#	lineWithMarg = subprocess.check_output(grepCommand, shell=True)
#	print(lineWithMarg)
#	varAndMarg = lineWithMarg.split()
#	print varAndMarg
#	return float(varAndMarg[1])

#	resultfile_i = open(resultMargBaseStr + str(j), "r")
#	for line in resultfile_i:
#		

def computeMargForGPs(mln, result, test, mpDict):
	testdb = open(test, "r+")
 	last_pos = testdb.tell()	
	line = testdb.readline()
	while line != '':
		print("curr line: " + line)
		if line.strip():
			#do stuff with the line
			query = line.split("(",1)[0]
			print(query)
			commentedOut = "//" + line[2:]
			#go back to beginning
			testdb.seek(last_pos)
			#overwrite with new line
			testdb.write(commentedOut)
			#get marg prob with commented out line
		#	predProbs[line] = getMargProb(query, )
	                margProb = getMargProb(mln, result, test, query, line)
			print("commented out version: " + commentedOut)
			#replace commented out line with old line
			testdb.seek(last_pos) #back before line
			testdb.write(line)	
			#now we're ready to call readline again, but 
			#first store new last position so we can overwrite
			#that line appropriately
		else:
			print("ignoring blank line")
		last_pos = testdb.tell()
		line = testdb.readline()

# capture the marginal probabilities calculated from these parity constraints
#		resultfile_i = open(resultMargBaseStr + str(j), "r")
#		for line in resultfile_i:
#			varAndMarg = line.split()
#			print varAndMarg
#			margProbs[varAndMarg[0]] += float(varAndMarg[1])



if __name__ == '__main__':
	main()	
