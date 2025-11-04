### FileThread 2025.08.08

# REQ: https://github.com/cduck/drawsvg/blob/master/docs/index.md

# import re
import sys
import os
import math
import hexdump
import drawsvg as draw
# import numpy as np

### arrays and variables
colors=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']

hexDumpArray=[]
matchesArray=[]
threadArray=[]
# scoreMatrix=[]
bestPath=[]
filesArray=[]

minRange = 32 # smallest matching region in bytes
maxRange = 10240 # 10k ought to be enough for anyone
HSize = 1500
VSIZE = 1000 # 3:2 aspect ratio for the output image.
Padding = 50

### SETUP
threadMode = sys.argv[1]
outputFile = sys.argv[2]

for argNum in range(3,len(sys.argv)):
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
	global hexFactor

	VScale = 1

	### Convert binary data to hex
	for fileNum in range(0,len(filesArray)):
	
		print(filesArray[fileNum])

# skip this and open as text if file is text?	
		if threadMode=="bin":
			binary=open(filesArray[fileNum],"rb").read()	
			hexDumpArray.append(hexdump.dump(binary).replace("00 00 ", "") )	# remove 00 padding in sparse data
			hexFactor = 3
			
		else: #threadMode=txt
			binary=open(filesArray[fileNum],"r").read()	
			hexDumpArray.append(binary)	# add text files as-is
			hexFactor = 1
		
		pVScale = VSIZE/(len(hexDumpArray[fileNum])/hexFactor) 	# fit the largest file vertically, but scale all files the same amount. 

# Can't do this with original binary size since some are 00 padded or "sparse"
		if pVScale < VScale:
			VScale = pVScale
			

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
		
		originLength = math.floor( (len(hexDumpArray[originFile])- hexFactor ) / hexFactor)
		
	
		print(f" {targetFile}/{len(hexDumpArray)}")
		while originByte < originLength :
	
			update_progress(originByte, originLength)
	
			for byteLength in range(minRange,10240):
		
				if int(originByte + byteLength) < int(originLength) : # don't try to read past the end. oof.
				
					charLength = int(hexFactor * byteLength) # searching for hexdump strings, so 3 chars per byte
					originChars = int(hexFactor * originByte) # searching for hexdump strings, so 3 chars per byte
							
					byteBlock = hexDumpArray[originFile][originChars:originChars+charLength] # block of bytes to search for

				# do the actual search	- just for the first instance
					wordIndex = hexDumpArray[targetFile].find(byteBlock)
							
					if wordIndex != -1:
						byteIndex = int(wordIndex/hexFactor)		
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
				
				byteIndex = int(wordIndex/hexFactor)

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
				originChars=int(blockMatch[x]) * hexFactor
				originFile=x-1
				charLength=blockMatch[0] * hexFactor
				byteBlock = hexDumpArray[originFile][originChars:originChars + charLength] # block of bytes to search for
				break

			
			
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
	d.save_png(outputFile +'.png')
	d.save_svg(outputFile +'.svg')

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