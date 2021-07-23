#!/usr/bin/env bash

homeDir=/mnt/zips/tmp/pythian/opentext/sow7/sar

# location of scripts and python scripts, outlier-remove.py and flatten.py
binDir=/mnt/zips/tmp/pythian/opentext/sow7/sar
export PATH="$binDir":$PATH

:<<'COMMENT'

walk through a directory structure of metrics files (ASM Metrics in this case)
and get moving average windows.

If the avg value of one of the the metrics exceeds a threshold, print a histogram 

assuming directory structure of

rac02
├── diskgroup-breakout
│   ├── GEN_DATA.csv
│   ├── GEN_FRA.csv
│   ├── GEN_REDOA.csv
...
rac02
├── diskgroup-breakout
│   ├── GEN_DATA.csv
│   ├── GEN_FRA.csv
│   ├── GEN_REDOA.csv
...


COMMENT


# ASM sampled once per minute
windowPeriod=60 # 60 minute windows
maxAllowedIOTime=0.25
maxAllowedIOTime=0.010
maxThresholdCount=30


for cluster in *-dbrac*
#for cluster in *-dbrac15
do
	> $cluster/${cluster}-high-IO-times.txt
	echo "##############################################"
	echo "cluster: $cluster"
	for dgCsvFile in $cluster/diskgroup-breakout/*.csv
	#for dgCsvFile in $cluster/diskgroup-breakout/MS1*.csv
	do
		echo "   ============================================"
		echo "   dgCsvFile: $dgCsvFile"
		hdrs="AVG_READ_TIME AVG_WRITE_TIME"
		cmdLine="./mvavg-max-detector.py $windowPeriod $maxAllowedIOTime $maxThresholdCount $hdrs < $dgCsvFile"
		echo "   CLI: $cmdLine"
		eval $cmdLine

		# returns a failure if data found
		if [[ $? -ne 0 ]]; then
			echo " ============================================"
			echo " == Histograms "
			echo " == Values are # of microseconds "
			echo " ============================================"
			# multiply by 1m to get integer
			echo " %%%% READ TIME %%%%"
			cut -f5 -d, $dgCsvFile | tail -n +2 | perl -e 'while(<STDIN>){print $_ * 1000000 . "\n"} '  | data-histogram.pl --bucket-count 10
			echo " %%%% WRITE TIME %%%%"
			cut -f6 -d, $dgCsvFile | tail -n +2 | perl -e 'while(<STDIN>){print $_ * 1000000 . "\n"} '  | data-histogram.pl --bucket-count 10

		fi

	done | tee -a $cluster/${cluster}-high-IO-times.txt

done

