
Dynachart
=========

See [sar-tools](https://github.com/jkstill/sar-tools) and its `asp.sh` script to generate CSV files from sar data.


## Overview

Dynachart reads CSV data from STDIN and produces a Microsoft Excel XLSX file containing data worksheets and embedded charts.
It is available in two implementations with identical command-line interfaces:

| Script | Language | Module |
|---|---|---|
| `dynachart.pl` | Perl | [Excel::Writer::XLSX](https://metacpan.org/pod/Excel::Writer::XLSX) |
| `dynachart.py` | Python 3 | [XlsxWriter](https://xlsxwriter.readthedocs.io/) |

Both scripts accept the same options and produce equivalent output.
The Python version is the recommended choice for new work.

### Why a Python version?

The Python XlsxWriter module is more actively developed than its Perl counterpart and exposes features
not yet available in `Excel::Writer::XLSX` — including richer conditional formatting, sparklines,
data tables, and additional chart customisation options.
These features will be incorporated into `dynachart.py` over time.


## dynachart.pl / dynachart.py

```text
  --help                  brief help message
  --man                   full documentation  (dynachart.pl only)
  --spreadsheet-file      output file name - defaults to asm-metrics.xlsx
  --worksheet-col         name of column used to segregate data into worksheets
                          defaults to a single worksheet if not supplied
  --chart-cols            list of columns to chart
  --chart-type            default chart type is 'line'
  --chart-titles          enable chart titles (default: on)
  --combined-chart        create a single chart rather than one chart per column
  --category-col          column for the X axis - a timestamp is typically used
                          the name must exactly match the header
  --secondary-axis-col    column to plot on a secondary Y axis (combined chart only)
  --legend-position       left, right, top, bottom - default is bottom
  --auto-filter-enabled   enable the drop-down Excel filters (default: on)
  --delimiter             input field delimiter - default is comma
  --list-available-columns  print column names from the header line and exit
  --debug                 enable debug output
```

### SYNOPSIS

```text
dynachart.pl [options]   (reads from STDIN)
dynachart.py [options]   (reads from STDIN)

Options:
  --help                  brief help message
  --spreadsheet-file      output file name - defaults to asm-metrics.xlsx
  --worksheet-col         name of column used to segregate data into worksheets
                          defaults to a single worksheet if not supplied
  --chart-cols            list of columns to chart; may be repeated or space-separated
                            --chart-cols col1 --chart-cols col2
                            --chart-cols col1 col2 col3
  --category-col          column to use as the X-axis category
                          typically a timestamp; defaults to the first column
  --combined-chart        create a single chart rather than one chart per column
  --delimiter             input field delimiter (default: comma)

dynachart accepts input from STDIN

dynachart.pl --worksheet-col DISKGROUP_NAME < my_input_file.csv
dynachart.py --worksheet-col DISKGROUP_NAME < my_input_file.csv

dynachart.pl --spreadsheet-file sar-disk-test.xlsx --combined-chart \
  --worksheet-col DEV --category-col 'timestamp' \
  --chart-cols 'rd_sec/s' --chart-cols 'wr_sec/s' < sar-disk-test.csv

dynachart.py --spreadsheet-file sar-disk-test.xlsx --combined-chart \
  --worksheet-col DEV --category-col 'timestamp' \
  --chart-cols 'rd_sec/s' 'wr_sec/s' < sar-disk-test.csv
```

### OPTIONS

```text
--help
        Print a brief help message and exit.

--spreadsheet-file
        The name of the Excel file to create.
        Default: asm-metrics.xlsx

--worksheet-col
        By default a single worksheet named DynaChart is created.
        When this option is supplied, the column value is used to segregate
        data into separate worksheets — one per unique value.

--chart-type
        Valid types: area, bar, column, line, pie, doughnut, scatter, stock
        Default: line

--chart-cols
        Columns to chart.  May be specified multiple times (one column per flag)
        or as a space-separated list in a single flag.

        eg.  --chart-cols READS --chart-cols WRITES
             --chart-cols READS WRITES BYTES

--category-col
        Column used as the category (X axis) in the chart.
        Defaults to the first column.  The name must exactly match the header.
        Typically this is a timestamp column.

--secondary-axis-col
        Plot one series column on a secondary Y axis.
        Only meaningful with --combined-chart.

--auto-filter-enabled / --no-auto-filter-enabled   (Python)
--auto-filter-enabled / --noauto-filter-enabled    (Perl)
        Enable or disable the Excel autofilter drop-downs.
        Default: enabled.

--delimiter
        Input field delimiter.  Default: comma.
        eg. --delimiter $'\t'   for tab-delimited input

--list-available-columns
        Print the column names found in the header line and exit.
        Useful for discovering the exact column names before charting.

--combined-chart / --no-combined-chart
        Create one combined chart containing all --chart-cols series
        instead of one chart per column.  Default: off.

--chart-titles / --no-chart-titles
        Include worksheet and column names as chart titles.  Default: on.

--legend-position
        Position of the chart legend: bottom (default), left, right, top.
```

### DESCRIPTION

Dynachart creates an Excel XLSX file with data worksheets and embedded charts
for selected columns.

A **Directory** worksheet is always created as the first sheet, containing
hyperlinks to every data worksheet for easy navigation.

Note: worksheet names are limited to 31 characters by Excel.
Device names longer than 31 characters are shortened by preserving the first
14 and last 14 characters with `...` in the middle.

Example: `scsi-360000970000192605774533030464644` →
`scsi-360000970...74533030464644`

### EXAMPLES

```text
# List available columns in a CSV file
dynachart.py --list-available-columns < sar-disk-test.csv

# One chart per metric, separate worksheets per device
dynachart.py --spreadsheet-file sar-disk.xlsx \
  --worksheet-col DEV --category-col timestamp \
  --chart-cols rd_sec/s --chart-cols wr_sec/s < sar-disk-test.csv

# Single combined chart
dynachart.py --spreadsheet-file sar-disk-combined.xlsx \
  --combined-chart --worksheet-col DEV --category-col timestamp \
  --chart-cols rd_sec/s wr_sec/s < sar-disk-test.csv

# Tab-delimited input
dynachart.py --delimiter $'\t' --spreadsheet-file output.xlsx \
  --category-col timestamp --chart-cols col1 col2 < data.tsv
```


---

## sar-chart.sh

Use `sar-chart.sh` to batch-generate Microsoft Excel spreadsheets from a directory of sar CSV files.

### Usage

```text
sar-chart.sh [options]

  -s  source directory for CSV files    (default: csv)
  -d  destination directory for XLSX files  (default: xlsx)
  -p  perl | python                     (default: perl)
  -h  show this help

Examples:

  sar-chart.sh
  sar-chart.sh -s /data/sar-csv -d /data/sar-xlsx
  sar-chart.sh -p python
  sar-chart.sh -s /data/sar-csv -d /data/sar-xlsx -p python
```

### Example session

```text
$ ./sar-chart.sh -p python -s csv -d xlsx
perlOrPython: python
srcDir: csv
destDir: xlsx
using python for charting
working on sar-network-device.xlsx
working on sar-network-error-device.xlsx
working on sar-network-nfs.xlsx
working on sar-network-nfsd.xlsx
working on sar-network-socket.xlsx
working on sar-context.xlsx
working on sar-cpu.xlsx
working on sar-cpu-combined.xlsx
working on sar-io-default.xlsx
working on sar-io-tps-combined.xlsx
working on sar-io-blks-per-second-combined.xlsx
working on sar-load-runq-threads.xlsx
working on sar-load-runq.xlsx
working on sar-memory.xlsx
working on sar-paging-rate.xlsx
working on sar-swap-rate.xlsx
working on sar-swap-utilization.xlsx
working on sar-kernel-fs.csv
```

### Example of a generated chart

<img src='https://github.com/jkstill/csv-tools/blob/master/dynachart/disk-chart-example.PNG' alt='Example: generated with dynachart' />
