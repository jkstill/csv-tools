
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


