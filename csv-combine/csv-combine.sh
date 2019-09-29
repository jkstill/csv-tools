#!/usr/bin/env bash

# simple shell script to combine CSV files
# it is assumed that files have header lines

set -u

declare -a csvFiles

#tail -n +2  csv/parameters_inst_1.csv >> parameters_all.csv
#tail -n +2  csv/parameters_inst_2.csv >> parameters_all.csv
#tail -n +2  csv/parameters_inst_3.csv >> parameters_all.csv

declare i=-1
for file in "$@"
do
	(( i++ ))
	csvFiles[$i]=$file
done

[[ $i -lt 0 ]] && {
	echo no files
	exit 1
}

declare lastFileID=${#csvFiles[@]}
(( lastFileID-- ))


head -1 ${csvFiles[0]}

for i in $(seq 0  $lastFileID)
do
	tail -n +2 ${csvFiles[$i]}	
done



