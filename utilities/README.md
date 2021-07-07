
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




