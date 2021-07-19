
Some CSV Utilities
==================

## csv2row.pl

Dump a CSV file, converting each field to a line with field number

```text

$  head -2 ../csv-combine/csv/parameters_inst_3.csv | ./csv2row.pl
1: "INSTANCE"
2: "NAME"
3: "DESCRIPTION"
4: "VALUE"
5: "ISDEFAULT"
6: "ISSES_MODIFIABLE"
7: "ISSYS_MODIFIABLE"
8: "ISMODIFIED"
9: "ISADJUSTED"
1: "3"
2: "DBFIPS_140"
3: "Enable use of crypographic libraries in FIPS mode
4:  public"
5: "FALSE"
6: "Y"
7: "N"
8: "N"
9: "N"
10: "N"

```

## csvhdr.pl

A simple shell script that calls csv2row.pl with the first line of a CSV file.

```text
>  ./csvhdr.sh ../csv-combine/csv/parameters_inst_3.csv
1: "INSTANCE"
2: "NAME"
3: "DESCRIPTION"
4: "VALUE"
5: "ISDEFAULT"
6: "ISSES_MODIFIABLE"
7: "ISSYS_MODIFIABLE"
8: "ISMODIFIED"
9: "ISADJUSTED"
```

## flatten.py

Remove extreme peaks from CSV data

`flatten.py   'tps'  'rtps'  'wtps'  < sar-io.cs`
  
## outlier-remove.py

Remove outliers from CSV data

`outlier-remove.py   'tps'  'rtps'  'wtps'  'bread/s'  'bwrtn/s' < sar-io.csv`

Combined with `flatten.py`:

```text
outlier-remove.py 'tps'  'rtps'  'wtps'  'bread/s'  'bwrtn/s' < /sar-io.csv \
  | flatten.py 'tps'  'rtps'  'wtps'  'bread/s'  'bwrtn/s' > sar-io-cleaned.csv
```

## mvavg-max-detector.py

For a series of data, get moving average for windowPeriod samples, iterarting through the data 1 row at a time.

The first argument is the window period

For instance, sar data is sampled 144 times a day

mvavg-max-detector.py window-size maxvalue threshold-count COL1 COL2 ... <  file

to find if either reads or writes are found to average > 0.5 seconds in a window sizes of 10 samples, at least 5 times

./mvavg-max-detector.py 10 0.5 5 AVG_READ_TIME AVG_WRITE_TIME < diskgroup-breakout/FRA.csv

If you want to get a count of all occurrences, make the threshold count larger than the number of rows in the file
Number of times MAX AVG_READ_TIME IO time of 0.5 in Window of 10 Exceeded: 11
Number of times MAX AVG_WRITE_TIME IO time of 0.5 in Window of 10 Exceeded: 10

./mvavg-max-detector.py 10 0.5 $(wc -l diskgroup-breakout/FRA.csv | awk '{ print $1}' )  AVG_READ_TIME AVG_WRITE_TIME < diskgroup-breakout/FRA.csv
Number of times MAX AVG_READ_TIME IO time of 0.5 in Window of 10 Exceeded: 146
Number of times MAX AVG_WRITE_TIME IO time of 0.5 in Window of 10 Exceeded: 10

## mvavg-max-detector.sh

This script is a driver for `mvavg-max-detector.py`


The scripts walk through a directory structure of metrics files (ASM Metrics in this case) and gets moving average windows.

If the avg value of one of the the metrics exceeds a threshold, print a histogram

Assuming a directory structure of

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

There are no parameters to pass, just modify values at the top of the script

When a threshold is exceeded, a histogram of the data is printed using [data-histogram.pl](https://github.com/jkstill/Histogram)

Just comment out that bit if you cannot, or do not care to install the histogram script.


## rising-rate-detector.py

Find a rate the is rising over time:

```text
rising-rate-detector.py 144 runq-sz plist-sz ldavg-1 ldavg-5 ldavg-15 blocked < rac10/rac10-p002/csv/sar-load.csv

plist-sz is rising
   avgFirstPeriod: 0.405740
  avgMiddlePeriod: 0.586150
    avgLastPeriod: 0.596348
       %increased:    47
```

Why a period of 144?  That is the number of daily SAR data samples. The 144 is used to compute a moving average.


## rising-rate-detector.sh

This is as shell script that calls `rising-rate-detector.py` for each CSV file in a directory structure.




