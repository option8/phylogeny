### FileThread 2025.08.08

# REQ: https://github.com/cduck/drawsvg/blob/master/docs/index.md


import re
import sys
import os
import math
import hexdump
import drawsvg as draw
import random
import numpy as np

import csv
 



### arrays and variables
colors=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']

hexDumpArray=[]
matchesArray=[]
threadArray=[]
# scoreMatrix=[]
bestPath=[]
filesArray=[]

minRange = 8 # smallest matching region in bytes
maxRange = 10240 # 10k ought to be enough for anyone
HSize = 1500
VSIZE = 1000 # 3:2 aspect ratio for the output image.
Padding=50


### SETUP

for argNum in range(1,len(sys.argv)):
	filesArray.append(sys.argv[argNum])

HScale = math.floor(HSize / len(filesArray))

d = draw.Drawing(HSize, VSIZE+Padding*2, origin=(-1*Padding,-1*Padding)) 

d.set_pixel_scale(1) # for converting SVG to PNG

d.append(draw.Rectangle(-1*Padding, -1*Padding, HSize, VSIZE+Padding*2 , fill='#FFFFFF')) # fill the canvas with white bg





### functions

def update_progress(progress,total):
	sys.stdout.write('\r[{0} of {1}]'.format(progress,total))
	sys.stdout.flush()


### RESET
def reset():
	matchesArray=[]
	threadArray=[]
# 	global scoreMatrix
	global filesArray
# 	scoreMatrix=[]

	global bestPath
	bestPath=[]
	global hexDumpArray
	hexDumpArray=[]

	global VScale

	VScale = 1

	### Convert binary data to hex
	for fileNum in range(0,len(filesArray)):
	
		print(filesArray[fileNum])

# skip this and open as text if file is text?	
		binary=open(filesArray[fileNum],"rb").read()
		
		hexDumpArray.append(hexdump.dump(binary).replace("00 00 ", "") )	# remove 00 padding in sparse data
		
		pVScale = VSIZE/(len(hexDumpArray[fileNum])/3) 	# fit the largest file vertically, but scale all files the same amount. 
														# Can't do this with original binary size since some are 00 padded or "sparse"
		if pVScale < VScale:
			VScale = pVScale
			
		# set up score matrix for sorting
# 		scoreMatrix.append([])
	
# 	while len(scoreMatrix[0]) < len(scoreMatrix): # make a square matrix
# 		for colNum in range(0,len(scoreMatrix)):
# 			scoreMatrix[colNum].append([])
#	print(scoreMatrix)


# for each pair of files, find matching segments.
# outputs matchArray and similarity scores

# score +1 per match
# score + # of bytes in match
# score - diff in match index
# 1/score = distance

def matchBlocks( matchType ):	

# 	global bestPath
# 	global scoreMatrix

#	print(scoreMatrix)

#	for originFile in range(0, len(hexDumpArray)):
	for originFile in range(0, len(hexDumpArray)-1):
		print(f" Completed {originFile} of {len(hexDumpArray)}") 
#		print(scoreMatrix[0])
# 		scoreMatrix[originFile][originFile]=0
		
#		for targetFile in range(originFile+1, len(hexDumpArray)):

		targetFile = originFile+1
		matchCount=0
		matchSum=0
		diffSum=0
		
		lastResult=""
		originByte=0
		originLength = math.floor( (len(hexDumpArray[originFile])-3 ) / 3)
		
		print(f" {targetFile}/{len(hexDumpArray)}")
		while originByte < originLength :
	
			update_progress(originByte, originLength)
	
			for byteLength in range(minRange,10240):
		
				if int(originByte + byteLength) < int(originLength) : # don't try to read past the end. oof.
				
					charLength = int(3 * byteLength) # searching for hexdump strings, so 3 chars per byte
					originChars = int(3 * originByte) # searching for hexdump strings, so 3 chars per byte
							
					byteBlock = hexDumpArray[originFile][originChars:originChars+charLength] # block of bytes to search for

				# do the actual search	- just for the first instance
					wordIndex = hexDumpArray[targetFile].find(byteBlock)
							
					if wordIndex != -1:
						byteIndex = int(wordIndex/3)		
						lastResult= f"{originFile}:{targetFile}\t{byteLength}\t{originByte}\t{byteIndex}"
						
					else:
								
						if len(lastResult) > 0: #success!

							currentMatch=[]
							currentMatch.append(byteLength-1)

							for i in range(0,originFile):
								currentMatch.append(None)

							currentMatch.append(originByte)

							for i in range(0, (targetFile - originFile) - 1):
								currentMatch.append(None)
							
							currentMatch.append(byteIndex)

							for i in range(targetFile, len(hexDumpArray)-1):
								currentMatch.append(None)
							
#								print(currentMatch)

							matchesArray.append(currentMatch)

							indexDiff=abs(byteIndex - originByte)
							if indexDiff > byteLength:
								indexDiff = byteLength/2
							elif indexDiff == 0:
								indexDiff = byteLength * 2
							else:
								indexDiff = byteLength
							
							matchCount+=1
							matchSum+=indexDiff
							lastResult="" # reset for next go-round
						break
				else: 
					break
				
				
			if len(lastResult) > 0:	### matched on end of file/bytesize loop
				
				byteIndex = int(wordIndex/3)

				currentMatch=[]
				currentMatch.append(byteLength-1)

				for i in range(0,originFile):
					currentMatch.append(None)

				currentMatch.append(originByte)

				for i in range(0, (targetFile - originFile) - 1):
					currentMatch.append(None)
				
				currentMatch.append(byteIndex)

				for i in range(targetFile, len(hexDumpArray)-1):
					currentMatch.append(None)

#					print(currentMatch)
				matchesArray.append(currentMatch)
				
				
### TBD: adjust scoring for byte offset differences					
				indexDiff=abs(byteIndex - originByte)
				if indexDiff > byteLength:
					indexDiff = byteLength/2
				elif indexDiff == 0:
					indexDiff = byteLength * 2
				else:
					indexDiff = byteLength
				
				matchCount+=1
				matchSum+=indexDiff
				
				lastResult="" # reset for next go-round
				
			originByte = originByte+(byteLength-2) # skip ahead past matched area, but overlap last 2 bytes 
		
# 		try:
# 			rowScore = math.sqrt( matchCount * matchSum )	## in case it's negative or 0.
# 		except:
# 			rowScore = 0
# 		finally:
# 			#scoreRow.append(rowScore)
# 			scoreMatrix[originFile][targetFile]=rowScore
# 			scoreMatrix[targetFile][originFile]=rowScore

	
#		scoreMatrix.append(scoreRow)


#	print(scoreMatrix)

# 	with open('filethread.csv', 'w', newline='') as file:
# 		writer = csv.writer(file)
# 		writer.writerows(scoreMatrix)
# 	pathsArray=[]
# 	pathLengthArray=[]

### what follows is all made redundant by pbzCompare.sh
# 	if matchType=="full":	
# 		for startNode in range(0,len(scoreMatrix)):
# 		
# 			# brute force nearest neighbors.
# 			# checklist = 0 - len(scoreMatrix)
# 			nodeList = [x for x in range(0, len(scoreMatrix))]
# 			# start with node 0
# 		#	startNode = 0
# 			pathLength = 0 
# 			currentNode = startNode
# 			currentPath = []
# 			
# 			while len(nodeList) > 0:
# 	#			print("NODES", nodeList)
# 				
# 	#			print(f"ROW {currentNode}", scoreMatrix[currentNode])
# 				
# 				# remove that from the checklist
# 				if currentNode in nodeList:
# 					nodeList.remove(currentNode)
# 					currentPath.append(currentNode)
# 				else:
# 					break
# 				
# 				# find nearest node in scoreMatrix
# 				# nextNode = scoreMatrix[currentNode].index(min(scoreMatrix[currentNode]))
# 				
# 				maxScore=0
# 
# 		
# 				for candidate in nodeList:
# 	#				print(scoreMatrix[currentNode][candidate])
# 		
# 					if scoreMatrix[currentNode][candidate] > maxScore:
# 						maxScore = scoreMatrix[currentNode][candidate]
# 						nextNode = candidate
# 				
# 	#			print("NEXT", nextNode, minScore)
# 				pathLength += maxScore
# 	
# 				currentNode = nextNode
# 	
# 			print(f"Path {startNode} {currentPath} length:", pathLength) ## all out of nodes?
# 			pathsArray.append(currentPath)
# 			pathLengthArray.append(pathLength)
# 
# 	
# 		bestPath=pathsArray[pathLengthArray.index(max(pathLengthArray))]
# 		print(f"Best path: {bestPath}")

# for each match found from file n to n+1, look for it in files n+2...
# blocklength, file0loc, file1loc, ...filenloc

def doThreads( matchType ):
	progress=0

	for blockMatch in matchesArray:
		progress+=1
		update_progress(progress, len(matchesArray))

# find first entry X with a value.
		for x in range(1,len(blockMatch)):
# originFile = X-1
			if blockMatch[x] is None:
				continue
			else:
				originChars=int(blockMatch[x]) * 3
				originFile=x-1
				charLength=blockMatch[0] * 3
				byteBlock = hexDumpArray[originFile][originChars:originChars + charLength] # block of bytes to search for
				break
### redundant, again, but also overkill and makes the display too messy.
# 		if matchType=="full":
# 			for targetFile in range(0,len(hexDumpArray)):
# 				if blockMatch[targetFile+1]==None:
# 					wordIndex=hexDumpArray[targetFile].find(byteBlock)
# 					if wordIndex != -1:
# 						byteIndex = int(wordIndex/3)
# 	#					print("found new match in ",targetFile+1)
# 					else:
# 						byteIndex = -1
# 					
# 					blockMatch[targetFile+1]= byteIndex
			
			
def drawThreads() :
	print(" Generating graph.")
	
	for fileNum in range(0,len(filesArray)):
			# draw rectangles
		emptyRect = draw.Rectangle(fileNum * HScale , 0, 10, VSIZE , fill='#CCCCCC', stroke='#000000', stroke_width=1)
		d.append(emptyRect)
	
		# Draw text labels
		line = draw.Line(fileNum * HScale - 2, VSIZE, fileNum * HScale - 2, 0, stroke='none')
		d.append(line)
		d.append(draw.Text(os.path.basename(filesArray[fileNum]), 20, path=line, text_anchor='start'))

	
	colorIndex=0	# for rotating through color palette
	# draw transparent polygon between right side of origin and left side of destination
	progress=0
	for matchArray in matchesArray:
		progress+=1
		update_progress(progress, len(matchesArray))

# 		global colorIndex		
	
# 		fillColor=colors[colorIndex]
		boxHeight=matchArray[0]*VScale

		for matchNum in range(1, len(matchArray)):
#			print(matchArray[matchNum])

			fillColor=colors[colorIndex] #matchNum]

			if matchArray[matchNum] != None:
				
				CoordY = matchArray[matchNum]* VScale
			# x, y, width, height
				d.append(draw.Rectangle( HScale * (matchNum - 1), CoordY, 10, boxHeight, fill=fillColor, stroke_width='none', fill_opacity=.5))

		for matchNum in range(1,len(matchArray)-1): # draw lines back from ends
			fillColor=colors[colorIndex] #matchNum]
#			print(matchArray[matchNum], matchArray[matchNum+1])
			if (matchArray[matchNum] != None ) and (matchArray[matchNum+1] != None ):
				CoordY = matchArray[matchNum]* VScale
				CoordY2 = matchArray[matchNum+1]* VScale
				d.append(draw.Lines(
					HScale*(matchNum-1) + 10, CoordY, 
					HScale*(matchNum), CoordY2, 
					HScale*(matchNum), boxHeight + CoordY2, 
					HScale*(matchNum-1) + 10, CoordY + boxHeight,
					stroke_width='none', fill=fillColor, close='true', fill_opacity=.25))
						
		colorIndex+=1
		if colorIndex == len(colors):
			colorIndex=0
	d.save_png('filethread.png')
	d.save_svg('filethread.svg')

### redundant
def reorderFiles():
	global filesArray
	global bestPath
	print(bestPath)
#	print("Before", filesArray)
	filesArray[:] = [filesArray[i] for i in bestPath]
#	print("After", filesArray)


reset()
matchBlocks( "fast" ) # "fast" is optomistic...
doThreads( "fast" )
drawThreads( )