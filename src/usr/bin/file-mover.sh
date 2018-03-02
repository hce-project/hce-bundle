#!/bin/bash

SOURCE_DIR=$1
DIST_DIR=$2
LEVELS=$3
TEMPLATE=$4
SILENT_MODE=$5
ARCHIVE=$6

printUsageAndExit()
## $1 - error message string
{
	printf "\nBad command line param. $1\nUsage: %s <source_dir> <dest_dir> <len_list> [<template>] [<silent_mode>] [<archive>]\n" $0
	echo "     <source_dir>   - source directory name"
	echo "     <dest_dir>     - destination directory name"
	echo "     <len_list>     - list of comma separated numbers - represents substrings size from file name to create tree of target directories"
	echo "     <template>     - template of file names for moving"
	echo "     <silent_mode>  - boolean if 1 then use in silent mode without any output messages"
 	echo "     <archive>      - boolean if 1 then gzip destination file"
	exit 1
}

createDir()
## $1 - directory name for creation if necessary
{
	if [ ! -d $1 ]
	then
		mkdir $1
	fi
}

if [ -z "$SOURCE_DIR" ]
then
	printUsageAndExit "Mandatory must be first argument source directory name for moving files."
fi

if [ -z "$DIST_DIR" ]
then
	printUsageAndExit "Mandatory must be second argument distanation directory name for moving files."
fi

if [ -z "$LEVELS" ]
then
	printUsageAndExit "Mandatory must be third argument csv list of numbers."
fi

if [ -z "$TEMPLATE" ]
then
	TEMPLATE="*"
fi

if [ -z "$SILENT_MODE" ]
then
	SILENT_MODE="0"
fi

if [ -z "$ARCHIVE" ]
then
	ARCHIVE="0"
fi

levels=()
OLDIFS=$IFS
IFS=', ' read -a levels <<< "${LEVELS[@]}"
IFS=$OLDIFS

LENGTH="0"
## Calculate allowed length of file name
for level in "${levels[@]}" 
	do
		if [ ! -z $level ]
		then
			levs=() 
			OLDIFS=$IFS
			IFS=':' read -a levs <<< "${level[@]}"
			IFS=$OLDIFS
	
			if [ ${#levs[*]} -eq "2" ]
			then
				level=${levs[1]}
			fi
			LENGTH=$(($LENGTH+$level))
		fi
	done

createDir "$DIST_DIR"

FILES=("$SOURCE_DIR"/$TEMPLATE)	
FILES=("${FILES[@]##*/}")

for file in "${FILES[@]}" 
	do
		if [ ! -d "$SOURCE_DIR/$file" ]
		then
			SUB_STR=${file%%.*}  
			SUB_LEN=${#SUB_STR}

			if [ $SUB_LEN -lt $LENGTH ]
			then
				if [ "$SILENT_MODE" -ne "1" ]
				then
					echo "Name file: '$file' too short"
				fi
			else
				path=$DIST_DIR
				START_POS=0
				for level in "${levels[@]}" 
					do
						levs=() 
						OLDIFS=$IFS
						IFS=':' read -a levs <<< "${level[@]}"
						IFS=$OLDIFS

						if [ ${#levs[*]} -eq "2" ]
						then
							START_POS=${levs[0]}
							level=${levs[1]}
						fi

						STOP_POS=$level
						SUB_STR=${file:$START_POS:$STOP_POS}
						START_POS=$(($STOP_POS+$START_POS))

						SUB_STR="${SUB_STR%%.*}"  
								
						path="$path/$SUB_STR"
						createDir "$path"					

					done
					
				mv "$SOURCE_DIR/$file" "$path/$file"

				if [ "$ARCHIVE" -eq "1" ]
				then
					gzip -f "$path/$file"	
				fi
			fi
		fi
	done 

exit 0

