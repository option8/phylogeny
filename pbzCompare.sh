#!/bin/zsh
zmodload zsh/mathfunc

binDir=$(dirname $0)
workingDir=$(pwd)

IFS=$'\n'
pathsArray=()

arrayIndex=1

echo "$# Files:"

for fileNum in $(seq 1 $#)
do
	
	DSKFile=${argv[$fileNum]}
	
	cat "$DSKFile" | pbzip2 -c > "/tmp/Temp1"
	
	StartZ=$(stat -f %z "/tmp/Temp1")
		
	for AdditionalNum in $(seq 1 $#)
	do

		AdditionalDSK=${argv[$AdditionalNum]}
#		printf "${DSKFile} :: ${AdditionalDSK} = "

		if [[ $AdditionalNum -eq $fileNum ]]
		then
			comboScore=1.0
		else

			cat "$AdditionalDSK" | pbzip2 -c > "/tmp/Temp2"
	
			EndZ=$(stat -f %z "/tmp/Temp2")
			
			CompCat=$(($StartZ + $EndZ))
	
			cat "$DSKFile" "$AdditionalDSK" | pbzip2 -c > "/tmp/TempZ"
			comboScore=$(( (1.0000 * $(stat -f %z "/tmp/TempZ")/CompCat) ))
		fi
		
		pathsArray[$arrayIndex]="$comboScore"
		
		printf ". "
		
		arrayIndex=$((arrayIndex+1))		
	done

	printf "\n"


done


bestPath=$(python3 $binDir/findPath.py $pathsArray)

parts=(${(@s: :)bestPath})

echo "Reordered:"

for i in $parts
do
	threadsArgument+=$(printf " \"$workingDir/${argv[$i+1]}\" ")
done

eval "python3 $binDir/filethread.py $threadsArgument"