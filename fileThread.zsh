#!/bin/zsh

# This requires both zsh and pbzip2
# Install it with
# 	brew install pbzip2
# This scheme will work with gzip, pkzip, among others - but pbzip is most consistent in my testing.
# Based on concepts explained pretty well in this video:
#	https://youtu.be/aLaYgzmRPa8?si=3t9V86oC-DqTrFyT

doHelp() {

cat << EOF
Command Line options:	
 -b		parse as binary (default)
 -t		force parsing as text
 -o [filename]	generates filename.svg (default "File-Ogeny.svg")
 -r		reorders (default) and reverses result
 -s		skips the pathfinding step, parses files in order they are given (overrides -r)
 -m [integer]	minimum size (characters/bytes) of matching regions (default 8)
 -h		print this help
 -p		just print out phylogeny distance matrix, suitable for analysis here:
		https://www.trex.uqam.ca/index.php?action=trex&menuD=1&method=2
	
EOF
	exit 0



}


if [[ "$#" -eq 0 || "$0" == "-h" ]]
then

	doHelp
	
fi



zmodload zsh/mathfunc

binDir=$(dirname $0)
workingDir=$(pwd)
IFS=$'\n'
pathsArray=()
arrayIndex=1

TEMPDIR=$(mktemp -d -t fileThread)

zparseopts -D -E -F -K -- b+=doBinary t+=doText o:=outputFile s+=skipReorder r+=reverseReorder m:=minBytes p+=doPhyloTree h+=showHelp
### -b			parse as binary (default)
### -t			force parsing as text
### -o [filename]	generates filename.svg (default "File-Ogeny.svg")
### -r			reorders and reverses result
### -s			skips the pathfinding step, parses files in order they are given (overrides -r)
### -m [integer]	minimum size of matching regions (default 8)
### -h			print this help 
### -p			just print out phylogeny distance matrix

### TODO: rename inputs with MD5 hash, sort out exact dupes

if [[ ! $(which pbzip2) ]]
then
	echo "This tool requires pbzip2"
	echo "Install it with\n\tbrew install pbzip2"
	exit 0
fi


outputFile=$outputFile[-1] # either provided on the command line, or default path
minBytes=$minBytes[-1]

if [[ -z $outputFile ]] 
then
	outputFile="File-Ogeny.svg"
fi

if [[ ${${outputFile##*.}:l} != "svg" ]]
then
	outputFile="$outputFile.svg"
fi

if [[ -z $minBytes ]] 
then
	minBytes=8
fi

if [[ ${#showHelp} -gt 0 ]]
then
	doHelp
fi


if [[ ${#doText} -gt 0 ]]
then
	threadMode="txt"
	# with each file in the command line to test
	for fileNum in $(seq 1 $#)
	do
		TESTFile=${argv[$fileNum]}
		TEMPFile="$TEMPDIR/"$(echo $TESTFile | tr -c "[:alnum:]" ".")
		echo "Preprocessing text file $TESTFile >> $TEMPFile"
		cat $TESTFile | tr "[:lower:]" "[:upper:]" | tr -cd "[:alnum:]" > "$TEMPFile"
		argv[$fileNum]=$TEMPFile
		threadMode="txt"

	done
else # default
	threadMode="bin"
fi




if [[ ${#skipReorder} -gt 0 ]]
then
	reorder="skip"
	pathsArray=({0..$(($# * $#))})
else 	
	if [[ ${#reverseReorder} -gt 0 ]]
	then
		reorder="reverse"
	else
		reorder="true"
	fi
	
	echo "$# Files to consider."
	# with each file in the command line to test
	TreeRows=()

	for fileNum in $(seq 1 $#)
	do

		TESTFile=${argv[$fileNum]}
		TreeRows[fileNum]=""
		# compress it into a temp file with pbzip2
		cat "$TESTFile" | pbzip2 -c > "$TEMPDIR/Temp1"
		
		StartZ=$(stat -f %z "$TEMPDIR/Temp1")
			
		for AdditionalNum in $(seq 1 $#)
		do
			# combine each candidate file with every other file in the list
			AdditionalTEST=${argv[$AdditionalNum]}
	#		printf "${TESTFile} :: ${AdditionalTEST} = "
	
			# score is "similarity" from 0 to 1. Same file? Score == 1.
			if [[ $AdditionalNum -eq $fileNum ]]
			then
				comboScore=1.0
			else
				# first compress additional file by itself.
				cat "$AdditionalTEST" | pbzip2 -c > "$TEMPDIR/Temp2"
				
				# get the compressed size
				EndZ=$(stat -f %z "$TEMPDIR/Temp2")
				
				# get the combined filesize of the compressed files
				CompCat=$(($StartZ + $EndZ))
	
				# finally, combine the two uncompressed files, then compress that.
				cat "$TESTFile" "$AdditionalTEST" | pbzip2 -c > "$TEMPDIR/TempZ"
	
				# the similarity score is the ratio of the size of the combined compressed files and the sum of the separately compressed files
				comboScore=$(( (1.0000 * $(stat -f %z "$TEMPDIR/TempZ")/CompCat) ))
						
			fi
			
			# write that down.
			pathsArray[$arrayIndex]="$comboScore"
			TreeRows[fileNum]+="\t$comboScore"
			# show progress.
			printf ". "
			
			arrayIndex=$((arrayIndex+1))		
		done
		
		# show progress.
		printf "\n"
	
	done

fi

if [[ ${#doPhyloTree} -gt 0 ]] # just do the distance tree, no threading.
then

	echo "Paste distance matrix into https://www.trex.uqam.ca/index.php?action=trex&menuD=1&method=2"
	echo " === "
	
	echo $#
	for fileNum in $(seq 1 $#)
		do
			normalizedFile=$(basename "${argv[$fileNum]}" | tr -c "[:alnum:]" ".")
			echo "$normalizedFile\t$TreeRows[fileNum]"
	done

else
	
	echo "Finding threads. Smallest region: $minBytes Bytes."
	
	# run the magic python "shortest path" script
	python3 $binDir/findPath.py $reorder $threadMode $outputFile $minBytes ${argv[@]} $pathsArray
	
	open -a Google\ Chrome ${outputFile}

fi