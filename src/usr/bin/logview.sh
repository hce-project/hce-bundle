#!/bin/bash

CRITERION=$1
TASK_SOURCE_DIR=$2
OUTPUT_FILE=$3
DELIMITER=$4

printUsageAndExit()
## $1 - error message string
{
	printf "\nBad command line param. $1\nUsage: %s <task_id> <task_source_dir> <out_file_name> [<delimiter>]\n" $0
	echo "     <criterion> - criterion for search. You can use some criterions, if you will be use '$DELIMITER' as delimiter"
	echo "     <task_source_dir> - task log directory contents source files for search"
	echo "     <out_file_name> - out result file name"
	echo "     <delimiter> - delimiter for criterions use few words"
	exit 1
}

if [ -z "$CRITERION" ]
then
	printUsageAndExit "Mandatory must be first argument criterion for search."
fi

if [ -z "$TASK_SOURCE_DIR" ]
then
	printUsageAndExit "Mandatory must be second argument source directory for search."
fi

if [ -z "$OUTPUT_FILE" ]
then
	printUsageAndExit "Mandatory must be third argument output file name for save result of search."
fi

if [ -z "$DELIMITER" ]
then
  DELIMITER="|||"
fi

removeFile()
## $1 - file name for remove
{
	if [ -e "$1" ]
	then
		rm -f $1
	fi
}

searchTaskData()
## $1 - criterion for search
## $2 - task log directory
## $3 - out file name
{
	local sed_queries=()
	local criterions=() 
	OLDIFS=$IFS
	IFS="$DELIMITER" read -a criterions <<< "$CRITERION"
	IFS=$OLDIFS
 
	local grep_query="grep -lrw '"
	a=0
	for one_criterion in "${criterions[@]}"
		do
			if [[ ! -z $one_criterion ]]
			then
				local sed_query="sed /";
				local params=($one_criterion)
				local params_size=${#params[@]}
				
##				echo "params: ${params[@]}"
##				echo "params_size: $params_size"
				i=1
				for param in "${params[@]}"
					do
						sed_query=("$sed_query""$param")
						
						if [ $i -lt $params_size ]
						then
							sed_query=("$sed_query"".")
						fi

						i=$(($i+1))
					done

				if [ $a -ne 0 ]
				then
					grep_query=("$grep_query""\|") 
				fi
	
				grep_query=("$grep_query""$one_criterion") 

				sed_query=("$sed_query""/!d")
##				echo "sed_query: $sed_query"
				sed_queries[$a]=$sed_query
				a=$(($a+1))
			fi		
		done

##echo "sed_queries: ${sed_queries[@]}"

	grep_query=("$grep_query""' $TASK_SOURCE_DIR")

	log_files=(`eval $grep_query`) 

##echo "found files: ${log_files[@]}"
##echo "files count: ${#log_files[*]}"

	if [[ "${#log_files[*]}" -eq 0 ]]
	then
		echo "No found files with content: $CRITERION"
	else
		echo "Found some files with content: '$CRITERION'" >> $OUTPUT_FILE
		echo " " >> $OUTPUT_FILE

		for log_file in "${log_files[@]}"
			do
				echo "$log_file content: " >> $OUTPUT_FILE
				echo " " >> $OUTPUT_FILE
				for sed_query in "${sed_queries[@]}"
					do
##						echo "Use  sed_query: $sed_query, log_file: $log_file"
						$sed_query "$log_file" >> $OUTPUT_FILE
					done
				echo " " >> $OUTPUT_FILE
			done
	fi
}

removeFile "$OUTPUT_FILE"

searchTaskData "$CRITERION" "$TASK_SOURCE_DIR" "$OUTPUT_FILE"

exit 0

