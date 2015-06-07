import sys
import os
import subprocess
from collections import defaultdict

def getMargProb(mln, result, test, query, gp):
	inferCommand = "./infer -ms -i " + mln + " -r " + result " -e " + test + " -q " + query
	os.system(inferCommand)
	varAndMarg = subprocess.check_output("grep " + result + " '" + gp + "' ")
	

def main():
	mln = sys.argv[1]
	result = sys.argv[2]
	test = sys.argv[3]
	
	predProbs = defaultdict(float)	

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
	                margProb = getMargProb(mln, result, test, query)
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

if __name__ == '__main__':
	main()	
