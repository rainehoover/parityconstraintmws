import sys
import os
import subprocess
from collections import defaultdict
import math

def main():
	n = int(sys.argv[1])
	k = int(sys.argv[2])	
	m = int(sys.argv[3])
	A = int(sys.argv[4])
	print n, k, m, A
	mln = sys.argv[5]
	resBaseStrWt = sys.argv[6]
	train = sys.argv[7]
 	lwQuery = sys.argv[8]
	test = sys.argv[9]
	resBaseStrMg = sys.argv[10]
	
	###* Learning weights *###

	weights = defaultdict(float)

	print("Number of A's to be created: " + str(A))

	#for each matrix A	
	for i in range(A):
		#make A
		makeClausesCommand = "python ./makeclauses.py " + str(n) + " " + str(k) + " " +str(m) + "     " + str(i)
		os.system(makeClausesCommand)
		#get weights learned from this perturbed distribution (perturbed by this A)
		getWeightsCommand = "./learnwts -d -i " + mln + " -o " + resBaseStrWt + str(i) + " -t     " + train + " -ne " + lwQuery
#		os.system(getWeightsCommand)
		#add weights to running total, to be averaged in the end
		weightsFilei = open(resBaseStrWt + str(i), "r")
		line = weightsFilei.readline()
		while line != '':
			if (line[0].isdigit()):
				tokens = line.split(" ", 1)
				weights[tokens[1].strip()] += float(tokens[0])
			line = weightsFilei.readline()
	#take the average over all i's
	print weights
	weights.update({k: v/A for k, v in weights.items()})
	print weights

	###* Write averaged weights to file *###
	wtsResult = open("cumulative-out.mln", "w+")
	wtsFile = resBaseStrWt + str(A-1)
	print wtsFile
	wtsTemplate = open(wtsFile, "r+")
	line = wtsTemplate.readline()
	print line
	while not line[0].isdigit():
		wtsResult.write(line)
		line = wtsTemplate.readline()
		print line
	wtsResult.write("\n")
	for x,y in weights.items():
		weightFormula = str(y) + " " + x + "\n"
		print weightFormula
		wtsResult.write(weightFormula)
	wtsTemplate.close()
	wtsResult.close()

	###* Inferring for each ground predicate *###

	#ground predicate j --> sum of marg probs with this predicate excluded over all Ai's
	margProbs = defaultdict(float)
	
	print("Number of ground predicates: " + str(n))
	
	#for each ground predicate
	numGPDict = defaultdict()
	numGPDict['Smokes'] = 8
	numGPDict['Friends'] = 28
	numGPDict['Cancer'] = 6
	computeMargForGPs(mln, resBaseStrMg, test, margProbs, numGPDict, A, k, m)
	finalSum = 0.0
	for mp in margProbs.values():
		finalSum += math.log(mp)
	print("OMG FINAL SUM: " + str(finalSum))
#	inferCommand = "./infer -ms -i cumulative-out.mln -r " + resBaseStrMg + str(i) + " -e " + test + " -q Friends"
#	print(" HELLO THIS IS THE INFER COMMAND POIT: " + inferCommand)
#	os.system(inferCommand)

'''
	for gp in range(n):
		#number of gps for this particular gp's template predicate (i.e. Smokes(John) --> Smokes has 3 gps)
		query = line.split("(",1)[0]
		print query
		gpn = numGPDict[query]
		#for every A	
		for i in range(A):
			makeClausesCommand = "python ./makeclauses.py " + str(gpn) + " " + str(k) + " " +str(m) + "     " + str(i)
			os.system(makeClausesCommand)
			computeMargForGPs(mln, result, test, margProbs)
'''

def getMargProb(mln, result, test, query, A, k, m, gpNum, mpDict, gp):
	#for each Ai
	for i in range(A):
		#make this Ai
		makeClausesCommand = "python ./makeclauses.py " + str(gpNum) + " " + str(k) + " " +str(m) + " " + str(i)
		print(makeClausesCommand)
		os.system(makeClausesCommand)
		resultName = result + str(i)
		#run infer on this perturbed distribution with Ai, using averaged weights
		inferCommand = "./infer -ms -i cumulative-out.mln -r " + resultName + " -e " + test + " -q " + query
		os.system(inferCommand)
		#grep for gp in result file and add in i's contribution to average marginal over all A's
		grepString = "grep '" + gp.replace(" ","") + "' " + resultName
		print(grepString)
		varAndMarg = subprocess.check_output(grepString, shell=True)
		print("Var and marg: " + varAndMarg)
		varAndMargArr = varAndMarg.split()
		print varAndMargArr
		mpDict[varAndMargArr[0]] += float(varAndMargArr[1])
	print mpDict
	mpDict.update({k: v/A for k, v in mpDict.items()})
	print mpDict

#loop over all the grounded predicates in the test database file
def computeMargForGPs(mln, result, test, mpDict, numGPDict, A, k, m):
        testdb = open(test, "r+")
        last_pos = testdb.tell()
        line = testdb.readline()
        while line != '':
                print("curr line: " + line)
                if line.strip(): #if it's not a blank line
                        #get the query value to pass to infer
			query = line.split("(",1)[0]
			#number of variables involved in A for this query
			gpNum = numGPDict[query]
                        commentedOut = "//" + line[2:]
                        #go back to beginning
                        testdb.seek(last_pos)
                        #overwrite with new line
                        testdb.write(commentedOut)
			testdb.close()
                        #get marg prob for this grounded predicate over all As generated
                        getMargProb(mln, result, test, query, A, k, m, gpNum, mpDict, line.strip())
                        #replace commented out line with old line
			testdb = open(test, "r+")
                        testdb.seek(last_pos) #back before line
                        testdb.write(line)
                else:
                        print("ignoring blank line")
		#now we're ready to call readline again, but 
                #first store new last position so we can overwrite
                #that line appropriately
                last_pos = testdb.tell()
                line = testdb.readline()
	
if __name__ == '__main__':
	main()
