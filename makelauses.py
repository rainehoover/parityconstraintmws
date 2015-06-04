import numpy
import sys
import random

		
def main():
	outfile = sys.argv[1] # where to write the clauses to (e.g. "out.txt")
	n = int(sys.argv[2]) # number variables
	k = int(sys.argv[3]) # number variables per constraint
	m = int(sys.argv[4]) # number constraints to add
	i = int(sys.argv[5])
	A,b = init(n,k,m)
	# clauses = printClausesForLine(A[0][:],b[0])
	
	## for loop here over rows of A
	allClauses = []
	for i in range(m):
		clauses = makeClauses(A[i][:],b[i])
		for clause in clauses:
			allClauses.append(clause)
	with open(outfile, "w") as f:
		for clause in allClauses:
			f.write(clause + "\n")
	with open(outfile + "_" + str(i), "w") as f:
		for clause in allClauses:
			f.write(clause + "\n")
	print "Here are the assignments to 0-th constraint in A which SAT b"
	clauses = makeClauses(A[0][:],b[0])
	for clause in clauses:
		print clause
	
def makeClauses(row_A,b):
	xorLine = [i for i in range(len(row_A)) if row_A[i] != 0]
	literal = xorLine[0]
	xorLine.remove(literal)
	currClauses = [[str(literal)],["-"+str(literal)]] # NOTE FIRST INDEX FOR A CLAUSE IS NUM NEG LITERALS IN CLAUSE
	for i in xrange(len(xorLine)):
		literal = xorLine[i]
		if literal != xorLine[len(xorLine)-1]:
			newClauses = []
			for clause in currClauses:
				newClauseTrueLiteral = list(clause)
				newClauseTrueLiteral.append(str(literal))
				newClauseFalseLiteral = list(clause)
				newClauseFalseLiteral.append("-"+str(literal))
				newClauses.append(newClauseTrueLiteral)
				newClauses.append(newClauseFalseLiteral)
			currClauses = newClauses
		else: #last addition, dependent on length and curr num neg
			for clause in currClauses:
				if isTrue(list(clause)):
					if b == 0:
						clause.append(str(literal))
					else:
						clause.append("-"+str(literal))
				else:
					#isFalse
					if b == 0:
						clause.append("-"+str(literal))
					else:
						clause.append(str(literal))
	return currClauses

def isTrue(clause):
	currVal = True if clause[0][0]!='-' else False
	del clause[0]
	for literal in clause:
		literalVal = False if literal[0] == '-' else True
		if literalVal != currVal:
			currVal = True
		else:
			currVal = False
	return currVal

# def printClausesForLine(row_A,b):
# 	xorLine = [i for i in range(len(row_A)) if row_A[i] != 0]
# 	first = xorLine[0]
# 	# print xorLine, first
# 	xorLine.remove(first)
# 	originalLength = len(row_A)
# 	firstList = recurse(list(xorLine),[[str(first)]],0,b,originalLength)
# 	secondList = recurse(list(xorLine),[["!"+str(first)]],1,b,originalLength)
# 	#combine the two and return
# 	for clause in secondList:
# 		firstList.append(clause)
# 	return firstList

# def recurse(xorLine,currClauses,numNeg,b,originalLength):
# 	if len(xorLine) == 0:
# 		print "recurse returning base"
# 		print currClauses
# 		return currClauses
# 	currVar = xorLine[0]
# 	print "removing..."
# 	print xorLine, currVar
# 	xorLine.remove(currVar)
# 	print xorLine, currVar
# 	if len(xorLine) == 0:
# 		print "recurse returning non-base len 0"
# 		print currClauses
# 		if (originalLength%2==0 and numNeg%2==1) or (originalLength%2==1 and numNeg%2==0): #XOR of rest is false
# 			if b == 0:
# 				return appendLiteralToClauses(currClauses,"!"+str(currVar))
# 			else:
# 				return appendLiteralToClauses(currClauses,str(currVar))
# 		else: #XOR of rest is true
# 			if b == 0:
# 				return appendLiteralToClauses(currClauses,str(currVar))
# 			else:
# 				return appendLiteralToClauses(currClauses,"!"+str(currVar))
# 	firstList = recurse(list(xorLine),appendLiteralToClauses(currClauses,str(currVar)),numNeg,b,originalLength)
# 	secondList = recurse(list(xorLine),appendLiteralToClauses(currClauses,"!"+str(currVar)),numNeg+1,b,originalLength)
# 	for clause in secondList:
# 		firstList.append(clause)
# 	print "recurse returning non-base"
# 	print currClauses
# 	print xorLine,firstList
# 	return firstList

# def appendLiteralToClauses(currClauses,literal):
# 	newClauses = []
# 	# print currClauses
# 	for clause in currClauses:
# 		newClause = []
# 		for elem in clause:
# 			newClause.append(elem)
# 		newClause.append(literal)
# 		newClauses.append(newClause)
# 	# print newClauses
# 	return newClauses

def init(n,k,m):
	A = numpy.zeros((m,n),dtype=int)
	b = numpy.zeros((m,1),dtype=int)
	for i in range(m):
		toFlipOn = []
		while len(toFlipOn) < k:
			nextInt = random.randint(0,n-1) #this documentation is sketchy
			if nextInt not in toFlipOn:
				toFlipOn.append(nextInt)
		if numpy.random.random() >= 0.5:
			b[i] = 1
		for j in toFlipOn:
			A[i][j] = 1
	print "A= "
	print A
	print "b= "
	print b
	return A,b



if __name__ == '__main__':
	main()
