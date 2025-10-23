### find shortest distance from node to node
import re
import sys
import os
import math
import numpy as np

fullArray=[]
scoreMatrix=[]
pathsArray=[]
pathLengthArray=[]

for argNum in range(1,len(sys.argv)):
	fullArray.append(float(sys.argv[argNum]))
#	print(sys.argv[argNum])

matrixDimension = int(math.sqrt(len(fullArray)))

for rowNum in range(0, matrixDimension) :
	rowMatrix=[]
	for colNum in range(0, matrixDimension):
		matrixIndex=rowNum * matrixDimension + colNum
		rowMatrix.append(fullArray[matrixIndex])

	scoreMatrix.append(rowMatrix)
#	print(rowMatrix)


for startNode in range(0,matrixDimension):

	# brute force nearest neighbors.
	# checklist = 0 - len(scoreMatrix)
	nodeList = [x for x in range(0, matrixDimension)]
	# start with node 0
#	startNode = 0
	pathLength = 0 
	currentNode = startNode
	currentPath = []
	
	while len(nodeList) > 0:
#			print("NODES", nodeList)
		
#			print(f"ROW {currentNode}", scoreMatrix[currentNode])
		
		# remove that from the checklist
		if currentNode in nodeList:
			nodeList.remove(currentNode)
			currentPath.append(currentNode)
		else:
			break
		
		# find nearest node in scoreMatrix
		# nextNode = scoreMatrix[currentNode].index(min(scoreMatrix[currentNode]))
		
		minScore=float(2.0)

		for candidate in nodeList:
#				print(scoreMatrix[currentNode][candidate])

			if scoreMatrix[currentNode][candidate] < minScore:
				minScore = scoreMatrix[currentNode][candidate]
				nextNode = candidate
#			print(f"MinScore: {minScore}")
		
#			print("NEXT", nextNode, minScore)
		pathLength += minScore

		currentNode = nextNode

#	print(f"Path {startNode} {currentPath} length:", pathLength) ## all out of nodes?
	pathsArray.append(currentPath)
	pathLengthArray.append(pathLength)

bestPath=pathsArray[pathLengthArray.index(min(pathLengthArray))]

returnText=""

# results seem to be reversed based on chronological order. So reverse the results?
flippedPath = np.flip(bestPath)
for x in range(0, len(bestPath)):
	returnText+=str(flippedPath[x]) + " "

print(returnText)