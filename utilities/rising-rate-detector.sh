#!/usr/bin/env bash

homeDir=/mnt/zips/tmp/pythian/opentext/sow7/sar

# location of scripts and python scripts, outlier-remove.py and flatten.py
binDir=/mnt/zips/tmp/pythian/opentext/sow7/sar
export PATH="$binDir":$PATH

:<<'COMMENT'

assuming directory structure of

dbrac01/
  node-01/
  node-02/
dbrac02/
  node-01/
  node-02/
...

COMMENT


windowPeriod=144

for cluster in *-dbrac* 
do
	echo "##############################################"
	echo "cluster: $cluster"
	for server in "$cluster"/"$cluster"*
	do
		#echo "   ============================================"
		#echo "   server: $server"
		#cd $server
		for csvFile in $server/csv/*.csv
		do
			#echo "      $csvFile"
			hdrs=$(csvhdr.sh $csvFile| tail -n +4| awk '{ print $2 }' | xargs echo -n)
			cmdLine="rising-rate-detector.py $windowPeriod $hdrs < $csvFile"
			results=$(eval $cmdLine)

			if [[ $? -ne 0 ]]; then
				echo "   ============================================"
				echo "   server: $server"
				echo "cli: $cmdLine"
				echo "$results"
			fi

		done


		#cd $homeDir
	done
	echo "##############################################"
done

