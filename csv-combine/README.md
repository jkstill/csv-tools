
# Combine CSV Files

Here are two simple scripts for combining CSV files

## csv-combine.sh

This Bash script grabs the first line of the first file as a header.

Then the body of each file is read and written to STDOUT.

```bash

>  ./csv-combine.sh csv/{a,b,c}.csv
c1,c2,c3
file-a,test,data
file-b,test,data
file-c,test,data

```

There is no error checking in this script, so it will include the output of d.csv; this file has 1 too many columns

```bash
>  ./csv-combine.sh csv/{a,b,c,d}.csv
c1,c2,c3
file-a,test,data
file-b,test,data
file-c,test,data
file-d,test,data,extra
```


## csv-combine.pl

This Perl script will do similar to the bash script, but does have some minimal error checking

```bash
>  ./csv-combine.pl --help

csv-combine.pl


usage: csv-combine.pl - combine CSV files into a single file

   csv-combine.pl --has-header --use-header --csv-file file-1 --csv-file file-2

--csv-file     Formatted length of operation lines - defaults to 80
--has-header   Indicates that the first line of each file is header column names.
               Default is that headers are present
               Use --no-has-header to negate
--use-header   Indicate the output should include a header. Dev
--delimiter    Specify the field delimiter.  Default is a comma

examples here:

   csv-combine.pl --csv-file file-1.csv --csv-file file-2.csv --no-has-header
```

Invalid file name

```bash

>  ./csv-combine.pl --csv-file csv/a.csv -csv-file csv/b.csv --csv-file csv/x.csv

File csv/x.csv Not Found!

csv-combine.pl

```

Column Count Mismatch

```bash

>  ./csv-combine.pl --csv-file csv/a.csv -csv-file csv/b.csv --csv-file csv/d.csv
c1,c2,c3
file-a,test,data
file-b,test,data
Column Count Mismatch!

```


Success

```bash
>  ./csv-combine.pl --csv-file csv/a.csv -csv-file csv/b.csv --csv-file csv/c.csv
c1,c2,c3
file-a,test,data
file-b,test,data
file-c,test,data
```


