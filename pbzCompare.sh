#!/bin/zsh

# This requires both zsh and pbzip2
# Install it with
# 	brew install pbzip2
# This scheme will work with gzip, pkzip, among others - but pbzip is most consistent in my testing.
# Based on concepts explained pretty well in this video:
#	https://youtu.be/aLaYgzmRPa8?si=3t9V86oC-DqTrFyT

zmodload zsh/mathfunc

binDir=$(dirname $0)
workingDir=$(pwd)

IFS=$'\n'
pathsArray=()


arrayIndex=1

# command line switch for binary vs text parsing
zparseopts -D -E -F -K -- b+=doBinary t+=doText o:=outputFile
### -b				parse as binary (default)
### -t				parse as text
### -o filename		generates filename.PNG and filename.SVG 

outputFile=$outputFile[-1] # either provided on the command line, or default path

if [[ -z $outputFile ]] 
then
	outputFile="filethread"
fi

if [[ ${#doText} -gt 0 ]]
then
	threadMode="txt"
	# with each file in the command line to test
	for fileNum in $(seq 1 $#)
	do
		TESTFile=${argv[$fileNum]}
		TEMPFile="/tmp/"$(echo $TESTFile | tr -c "[:alnum:]" ".")
		echo "Preprocessing text file $TESTFile >> $TEMPFile"
		cat $TESTFile | tr "[:lower:]" "[:upper:]" | tr -cd "[:alnum:]" > "$TEMPFile"
		argv[$fileNum]=$TEMPFile
		threadMode="txt"

	done
else # default
	threadMode="bin"	
fi

echo "$# Files:"

# with each file in the command line to test
for fileNum in $(seq 1 $#)
do
	
	TESTFile=${argv[$fileNum]}

	# compress it into a temp file with pbzip2
	cat "$TESTFile" | pbzip2 -c > "/tmp/Temp1"
	
	StartZ=$(stat -f %z "/tmp/Temp1")
		
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
			cat "$AdditionalTEST" | pbzip2 -c > "/tmp/Temp2"
			
			# get the compressed size
			EndZ=$(stat -f %z "/tmp/Temp2")
			
			# get the combined filesize of the compressed files
			CompCat=$(($StartZ + $EndZ))

			# finally, combine the two uncompressed files, then compress that.
			cat "$TESTFile" "$AdditionalTEST" | pbzip2 -c > "/tmp/TempZ"

			# the similarity score is the ratio of the size of the combined compressed files and the sum of the separately compressed files
			comboScore=$(( (1.0000 * $(stat -f %z "/tmp/TempZ")/CompCat) ))
						
		fi
		
		# write that down.
		pathsArray[$arrayIndex]="$comboScore"
		
		# show progress.
		printf ". "
		
		arrayIndex=$((arrayIndex+1))		
	done
	
	# show progress.
	printf "\n"

done

# run the magic python "shortest path" script
bestPath=$(python3 $binDir/findPath.py $pathsArray)

# ingest the resulting list as an array, why not?
parts=(${(@s: :)bestPath})

echo "Reordered:"

# display and barf the list back out to the next python script
for i in $parts
do
#	threadsArgument+=$(printf " \"$workingDir/${argv[$i+1]}\" ")
	threadsArgument+=$(printf " \"${argv[$i+1]}\" ")
done

eval "python3 $binDir/filethread.py $threadMode $outputFile $threadsArgument"

open "${outputFile}.png"
