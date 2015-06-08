import sys
import os
import subprocess
from collections import defaultdict
import math
import pickle

def main():
	nVars = int(sys.argv[1])
	kVars = int(sys.argv[2])	
	mClauses = int(sys.argv[3])
	AMatrices = int(sys.argv[4])
	print(nVars, kVars, mClauses, AMatrices)
	mln = sys.argv[5]
	resBaseStrWt = sys.argv[6]
	train = sys.argv[7]
 	lwQuery = sys.argv[8]
	test = sys.argv[9]
	resBaseStrMg = sys.argv[10]
	query = sys.argv[11]
	iterating = int(sys.argv[12])
	threadId = int(sys.argv[13])
	resultDict = defaultdict(float) #keep k from 3 up, m from 4 up
	if iterating:
		for i in range(4, AMatrices + 1):
			for k in range(3, kVars + 1):
				print("n, k, m, i = "+ str(nVars), str(k), str(mClauses), str(i))
				runId = "n" + str(nVars) + "k" + str(k) + "m" + str(mClauses) + "A" + str(i)
				try:
					f = open('resultDict' + runId + '.p', 'r')
					print("Already got results for run " + runId + "\n")
					f.close()
				except IOError:
					runOnce(nVars, k, mClauses, i, mln, resBaseStrWt, train, lwQuery, test, resBaseStrMg, query, resultDict, runId, iterating, threadId)
	else:
		runId = "n" + str(nVars) + "k" + str(kVars) + "m" + str(mClauses) + "A" + str(AMatrices)
		print("not iterating this time\n")
		runOnce(nVars, kVars, mClauses, AMatrices, mln, resBaseStrWt, train, lwQuery, test, resBaseStrMg, query, resultDict, runId + '0', iterating, threadId)

def getWeights(n, k, m, A, mln, resBaseStrWt, train, lwQuery, test, runId):
	weights = defaultdict(float)
	print("runid: " + runId)
	for i in range(A):
		print("Getting weights for A #" + str(i) + "\n")
		#make A (n = 122 for uw, 10 for smoking)
		makeClausesCommand = "python ./makeclauses.py " + str(n) + " " + str(k) + " " +str(m) + " " + str(i)
		os.system(makeClausesCommand)
		#get weights learned from this perturbed distribution (perturbed by this A)
		getWeightsCommand = "./learnwts -d -i " + mln + " -o " + resBaseStrWt + runId + str(i) + " -t " + train + " -ne " + lwQuery
		os.system(getWeightsCommand)
		#add weights to running total, to be averaged in the end
		weightsFilei = open(resBaseStrWt + runId + str(i), "r")
		print("opened weightsFilei")
		line = weightsFilei.readline()
		while line != '':
			print line
			if (line[0].isdigit()):
				tokens = line.split(" ", 1)
				weights[tokens[1].strip()] += float(tokens[0])
			line = weightsFilei.readline()
		weightsFilei.close()
	#take the average over all i's
	print("HELLO NARF :")
	print weights
	weights.update({k: v/A for k, v in weights.items()})
	print weights
	pickle.dump(weights, open('avgWts' + runId + '.p', 'wb'))

	###* Write averaged weights to file *###
	wtsResult = open("cumulative-out.mln" + runId, "w+")
	wtsFile = resBaseStrWt + runId + "0" 
	print wtsFile
	wtsTemplate = open(wtsFile, "r+")
	line = wtsTemplate.readline()
	#print line
	while not line[0].isdigit():
		wtsResult.write(line)
		line = wtsTemplate.readline()
	#	print line
	wtsResult.write("\n")
	for x,y in weights.items():
		weightFormula = str(y) + " " + x + "\n"
	#	print weightFormula
		wtsResult.write(weightFormula)
	wtsTemplate.close()
	wtsResult.close()


def runOnce(n, k, m, A, mln, resBaseStrWt, train, lwQuery, test, resBaseStrMg, query, resultDict, runId, iterating, threadId):
	print("running run: " + runId + "\n")
	###* Learning weights *###
	print("Number of A's to be created: " + str(A))
	#try to open file of weights, if I can't, give up.
	try:
		#runId2 = ''
		#if not iterating:
		#	print("really not iterating!")
		#	runId2 += runId[:len(runId) - 1]
		#else:
		#	runId2 += runId
		wtsResult = open("cumulative-out.mln" + runId, "r")
		print("Already had weights for run " + runId + "\n")
		wtsResult.close()
	except IOError:
		print("Didn't already have weights for run " + runId + "\n")
		getWeights(n, k, m, A, mln, resBaseStrWt, train, lwQuery, test, runId)
	#for each matrix A	
	
	# non-edited version, for comparison- assume it has already been run on graphics.db
#	oobLearnWtsCommand = "../../../alchemy-2/bin/learnwts -d -i ../exdata/smoking.mln -o oob-out.mln -t ../exdata/smoking-train.db -ne Smokes,Cancer"
#	os.system(oobLearnWtsCommand)

	###* Inferring for each ground predicate *###
	#create the hardcoded dict with how many gp's are present in the mln for each infer run with each query
	numGPDict = defaultdict()
	numGPDict['Smokes'] = 8
	numGPDict['Friends'] = 28
	numGPDict['Cancer'] = 6
	numGPDict['advisedBy'] = 775

	#ground predicate j --> sum of marg probs with this predicate excluded over all Ai's
	margProbsRP = defaultdict(float)
	margProbsOOB = defaultdict(float)
	
	print("Number of ground predicates: " + str(n))
	
	
	#get the marginal probabilities for each gp
	computeMargForGPs(mln, resBaseStrMg, test, margProbsRP, numGPDict, A, k, m, margProbsOOB, query, runId, iterating, threadId)
	
#	pickle.dump(margProbsRP, open('mpsRP2' + str(A) + str(k) + str(m) + '.p', 'wb'))
#	pickle.dump(margProbsOOB, open('mpsOOB.p', 'wb'))

	#get the overall result
	finalSumRP = 0.0
	for mp in margProbsRP.values():
		finalSumRP += math.log(mp)
	print("FINAL SUM RP: " + str(finalSumRP))
	finalSumOOB = 0.0
	for mp in margProbsOOB.values():
		finalSumOOB += math.log(mp)
	print("FINAL SUM OOB: " + str(finalSumOOB))
	
	resultDict[(A, k, m)] = finalSumRP
	print resultDict
	pickle.dump(resultDict, open('resultDict' + runId + '.p', 'wb'))

def getMargProbRP(mln, result, test, query, A, k, m, gpNum, mpDict, gp, runId, iterating):
	#for each Ai
	for i in range(A):
		#make this Ai
		makeClausesCommand = "python ./makeclauses.py " + str(gpNum) + " " + str(k) + " " +str(m) + " " + str(i)
		print(makeClausesCommand)
		os.system(makeClausesCommand)
		resultName = result + str(i)
		#run infer on this perturbed distribution with Ai, using averaged weights
		if iterating:
			inferCommand = "./infer -ms -i cumulative-out.mln" + runId + " -r " + resultName + " -e " + test + " -q " + query
		else:
			inferCommand =  "./infer -ms -i cumulative-out.mln" + runId + " -r " + resultName + " -e " + test + " -q " + query
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

def getMargProbOOB(mln, result, test, query, gp, mpDict):
	resultName = result
	inferCommand = "../../../alchemy-2/bin/infer -ms -i uw-out.mln -r " + resultName + " -e " + test + " -q " + query
	print("OOB infer: " + inferCommand + "\n")
#	os.system(inferCommand)
	#grep for gp in result file and add in i's contribution to average marginal over all A's
	grepString = "grep '" + gp.replace(" ","") + "' " + resultName
	print(grepString)
	varAndMarg = subprocess.check_output(grepString, shell=True)
	print("Var and marg: " + varAndMarg)
	varAndMargArr = varAndMarg.split()
	print varAndMargArr
	mpDict[varAndMargArr[0]] += float(varAndMargArr[1])
	print mpDict

#loop over all the grounded predicates in the test database file
def computeMargForGPs(mln, result, test, mpDict, numGPDict, A, k, m, mpDictOOB, query, runId, iterating, threadId):
        test = test + str(threadId)
	print("test db: " + test)
	testdb = open(test, "r+")
        last_pos = testdb.tell()
        line = testdb.readline()
        while line != '':
                print("curr line: " + line)
                if line.strip(): #if it's not a blank line
                        #get the query value to pass to infer
			currp = line.split("(",1)[0]
			if currp == query:
			#number of variables involved in A for this query
				gpNum = numGPDict[query]
				commentedOut = "//" + line[2:]
				#go back to beginning
				testdb.seek(last_pos)
				#overwrite with new line
				testdb.write(commentedOut)
				testdb.close()
				#get marg prob for this grounded predicate over all As generated
				getMargProbRP(mln, result, test, query, A, k, m, gpNum, mpDict, line.strip(), runId, iterating)
#				getMargProbOOB(mln, result, test, query, line.strip(), mpDictOOB)
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
	testdb.close()

if __name__ == '__main__':
	main()
