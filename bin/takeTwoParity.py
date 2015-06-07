import sys
import os
import subprocess
from collections import defaultdict

def main():
	n = int(sys.argv[1])
	k = int(sys.argv[2])	
	m = int(sys.argv[3])
	A = int(sys.argv[4])
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
		#os.system(getWeightsCommand)
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
	for k,v in weights.items():
		weightFormula = str(v) + " " + k
		print weightFormula
		wtsResult.write(weightFormula)

	###* Inferring for each ground predicate *###

	#ground predicate j --> sum of marg probs with this predicate excluded over all Ai's
	margProbs = defaultdict(float)
	
	print("Number of ground predicates: " + str(n))
	
	#for each ground predicate
	numGPDict = defaultdict()
	numGPDict['Smokes'] = 8
	numGPDict['Friends'] = 28
	numGPDict['Cancer'] = 6
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

def getMargProb(mln, result, test, query):
	inferCommand = "./infer -ms -i " + mln + " -r " + result + " -e " + test + " -q " + query
	

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
                #       predProbs[line] = getMargProb(query, )
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
'''	
if __name__ == '__main__':
	main()
