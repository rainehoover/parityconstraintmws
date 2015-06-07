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
		os.system(makeClausesCommand)
		print("Made one A!")
		# now clauses.text holds clauses for this particular A
		getWeightsCommand = "./learnwts -d -i " + mln + " -o " + resultWtBaseStr + str(j) + " -t " + traindb + " -ne " + query
		print(getWeightsCommand)
		os.system(getWeightsCommand)
		# now the weights are present learned from this particular parity constraint
		inferCommand = "./infer -ms -i " + resultWtBaseStr + str(j) + " -r " + resultMargBaseStr + str(j) + " -e " + testdb + " -q " + query
		print(inferCommand)
		os.system(inferCommand)
		# capture the marginal probabilities calculated from these parity constraints
		resultfile_i = open(resultMargBaseStr + str(j), "r")
		for line in resultfile_i:
			varAndMarg = line.split()
			print varAndMarg
			margProbs[varAndMarg[0]] += float(varAndMarg[1])
		print margProbs
	
	#Now that we have results from all As, divide marg probs by number of A's to get average
	margProbs.update({k: v/i for k, v in margProbs.items()})	
	print margProbs
	finalOutput = open(resultMargBaseStr + "final", "w")
	for k, v in margProbs.items():
		finalOutput.write(k + " " + str(v) + "\n")

if __name__ == '__main__':
	main()
