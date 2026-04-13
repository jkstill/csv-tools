#!/usr/bin/env python3

# dynachart.py
# Jared Still 2017-07-23 (original Perl version)
# Python conversion 2026-04-13
# still@pythian.com jkstill@gmail.com

# Data is read from STDIN

import sys
import re
import argparse
import xlsxwriter


CHART_TYPES_AVAILABLE = ['area', 'bar', 'column', 'line', 'pie', 'doughnut', 'scatter', 'stock']
LEGEND_POSITIONS = ['bottom', 'left', 'right', 'top']


def parse_args():
    parser = argparse.ArgumentParser(
        prog='dynachart.py',
        description='Create an Excel file with charts from CSV data read on STDIN.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CHART TYPES:
  area, bar, column, line (default), pie, doughnut, scatter, stock

LEGEND POSITIONS:
  bottom (default), left, right, top

EXAMPLES:

  dynachart.py accepts data from STDIN

  dynachart.py --worksheet-col DISKGROUP_NAME --spreadsheet-file mywork.xlsx

  dynachart.py --spreadsheet-file sar-disk-test.xlsx --combined-chart \\
    --worksheet-col DEV --category-col timestamp \\
    --chart-cols rd_sec/s wr_sec/s < sar-disk-test.csv
        """,
    )

    parser.add_argument(
        '--spreadsheet-file',
        default='asm-metrics.xlsx',
        metavar='FILE',
        help='Output Excel file name (default: asm-metrics.xlsx)',
    )
    parser.add_argument(
        '--debug',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='Enable debug output (default: off)',
    )
    parser.add_argument(
        '--chart-cols',
        nargs='+',
        action='append',
        default=None,
        metavar='COL',
        help='One or more column names to chart; may be repeated',
    )
    parser.add_argument(
        '--chart-type',
        default='line',
        choices=CHART_TYPES_AVAILABLE,
        help='Chart type (default: line)',
    )
    parser.add_argument(
        '--secondary-axis-col',
        default='',
        metavar='COL',
        help='Column name to plot on secondary Y axis (combined chart only)',
    )
    parser.add_argument(
        '--auto-filter-enabled',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Enable Excel autofilter dropdowns (default: on; disable with --no-auto-filter-enabled)',
    )
    parser.add_argument(
        '--legend-position',
        default='bottom',
        choices=LEGEND_POSITIONS,
        help='Chart legend position (default: bottom)',
    )
    parser.add_argument(
        '--combined-chart',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='Create one combined chart for all --chart-cols instead of one chart per column',
    )
    parser.add_argument(
        '--chart-titles',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Add titles to charts (default: on; disable with --no-chart-titles)',
    )
    parser.add_argument(
        '--list-available-columns',
        action=argparse.BooleanOptionalAction,
        default=False,
        help='Print column names from the header line and exit',
    )
    parser.add_argument(
        '--worksheet-col',
        default='',
        metavar='COL',
        help='Column name whose values are used to segregate data into separate worksheets',
    )
    parser.add_argument(
        '--category-col',
        default='',
        metavar='COL',
        help='Column name to use as the X-axis category (typically a timestamp); defaults to first column',
    )
    parser.add_argument(
        '--delimiter',
        default=',',
        help='Input field delimiter (default: comma)',
    )

    return parser.parse_args()


def truncate_sheet_name(name):
    """Excel worksheet names are limited to 31 characters.
    When the name is longer, cut out the middle to preserve both ends."""
    if len(name) > 31:
        return name[:14] + '...' + name[-14:]
    return name


def coerce_numeric(val):
    """Convert a string to int or float if possible, otherwise return it as-is.
    xlsxwriter writes whatever Python type it receives, so without this
    conversion every split() value would be stored as text in Excel."""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


def main():
    args = parse_args()

    debug               = args.debug
    combined_chart      = args.combined_chart
    # action='append' + nargs='+' produces a list-of-lists; flatten it.
    # Supports both  --chart-cols a b c  and  --chart-cols a --chart-cols b
    chart_cols = [c for sublist in (args.chart_cols or []) for c in sublist]
    category_col_name   = args.category_col
    secondary_axis_col  = args.secondary_axis_col
    auto_filter_enabled = args.auto_filter_enabled
    chart_type          = args.chart_type
    chart_titles        = args.chart_titles
    legend_position     = args.legend_position
    delimiter           = args.delimiter
    xl_file             = args.spreadsheet_file
    worksheet_col       = args.worksheet_col
    list_available_columns = args.list_available_columns

    # ------------------------------------------------------------------
    # Read and parse the header line
    # ------------------------------------------------------------------
    header_line = sys.stdin.readline()
    if not header_line:
        print("Error: no input data on STDIN", file=sys.stderr)
        sys.exit(1)

    # Strip CR/LF (handle Windows line endings)
    header_line = header_line.rstrip('\r\n')

    # sadf starts header lines with '# ' — remove that prefix
    header_line = re.sub(r'^#\s+', '', header_line)

    # Split on delimiter followed by optional whitespace (matches Perl behaviour)
    labels = re.split(re.escape(delimiter) + r'\s*', header_line)

    if list_available_columns:
        print('\n'.join(labels))
        sys.exit(0)

    if debug:
        print("LABELS:")
        print('\n'.join(labels))
        print()

    # ------------------------------------------------------------------
    # Resolve the category (X-axis) column index
    # ------------------------------------------------------------------
    category_col_num = 0
    if category_col_name:
        if category_col_name in labels:
            category_col_num = labels.index(category_col_name)
        else:
            print(
                f"Warning: category column '{category_col_name}' not found in headers",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # Resolve the worksheet-segregation column position
    # ------------------------------------------------------------------
    worksheet_col_pos = None
    if worksheet_col:
        if worksheet_col in labels:
            worksheet_col_pos = labels.index(worksheet_col)
        else:
            print(
                f"Warning: worksheet column '{worksheet_col}' not found in headers",
                file=sys.stderr,
            )
            worksheet_col = ''

    if debug:
        print(f"worksheet_col_pos: {worksheet_col_pos}")

    # ------------------------------------------------------------------
    # Resolve chart column positions (preserves the order given on CLI)
    # ------------------------------------------------------------------
    chart_col_pos = []
    missing_chart_cols = []
    for col in chart_cols:
        if col in labels:
            chart_col_pos.append(labels.index(col))
        else:
            missing_chart_cols.append(col)

    if missing_chart_cols:
        print(
            f"Warning: the following chart columns were not found in the data: "
            f"{', '.join(missing_chart_cols)}",
            file=sys.stderr,
        )

    if chart_cols and not chart_col_pos:
        print(
            "Warning: none of the requested chart columns are available — "
            "the spreadsheet will be created without charts.",
            file=sys.stderr,
        )

    # ------------------------------------------------------------------
    # Validate secondary-axis column
    # ------------------------------------------------------------------
    if secondary_axis_col and secondary_axis_col not in labels:
        print(
            f"\n secondary axis column of '{secondary_axis_col}' is invalid"
            " - not using secondary axis",
            file=sys.stderr,
        )
        secondary_axis_col = ''

    if debug:
        print(f"worksheet_col: {worksheet_col}")
        print(f"chart_cols: {chart_cols}")
        print(f"chart_col_pos: {chart_col_pos}")
        print(f"labels: {labels}")

    # ------------------------------------------------------------------
    # Create workbook and formats
    # ------------------------------------------------------------------
    workbook = xlsxwriter.Workbook(xl_file)

    std_format = workbook.add_format({
        'bold': False,
        'font_name': 'Courier New',
        'font_size': 10,
        'font_color': 'black',
    })
    bold_format = workbook.add_format({
        'bold': True,
        'font_name': 'Courier New',
        'font_size': 10,
        'font_color': 'black',
    })

    # ------------------------------------------------------------------
    # Directory worksheet (first sheet — an index with hyperlinks)
    # ------------------------------------------------------------------
    directory_name = 'Directory'
    directory = workbook.add_worksheet(directory_name)
    directory.set_column(0, 0, 30)
    directory_row = 0
    directory.write_row(directory_row, 0, ['Directory'], bold_format)
    directory_row += 1

    # ------------------------------------------------------------------
    # Read data rows and populate worksheets
    # ------------------------------------------------------------------
    # line_counts[name] tracks the next available row index for each sheet
    line_counts = {}
    worksheets  = {}

    for line in sys.stdin:
        line = line.rstrip('\r\n')
        data = line.split(delimiter)

        # Determine which worksheet this row belongs to
        if worksheet_col and worksheet_col_pos is not None:
            curr_name = truncate_sheet_name(data[worksheet_col_pos])
        else:
            curr_name = 'DynaChart'

        if debug:
            print(f"Worksheet Name: {curr_name}")

        # Create the worksheet on first encounter
        if curr_name not in worksheets:
            ws = workbook.add_worksheet(curr_name)
            worksheets[curr_name] = ws
            line_counts[curr_name] = 0

            ws.write_row(line_counts[curr_name], 0, labels, bold_format)
            line_counts[curr_name] += 1

            # Freeze pane below the header row
            ws.freeze_panes(line_counts[curr_name], 0)

            # Autofilter on the header row
            if auto_filter_enabled:
                ws.autofilter(0, 0, 0, len(data) - 1)

        worksheets[curr_name].write_row(
            line_counts[curr_name], 0,
            [coerce_numeric(v) for v in data],
            std_format,
        )
        line_counts[curr_name] += 1

    if debug:
        print("Worksheets:", list(worksheets.keys()))
        print("line_counts:", line_counts)

    # ------------------------------------------------------------------
    # Create charts (skipped when no valid chart columns were resolved)
    #
    # Default mode: one chart per column listed in --chart-cols.
    # With --combined-chart: a single chart containing all series.
    #
    # Chart dimensions mirror the original Perl values:
    #   width  = 480 * 3 = 1440 px
    #   height = 23 rows * 18 px/row = 414 px
    # ------------------------------------------------------------------
    row_height   = 18   # pixels per row
    chart_height = 23   # chart height in rows
    chart_width  = 480 * 3

    for ws_name, ws in (worksheets.items() if chart_col_pos else []):
        if debug:
            print(f"Charting worksheet: {ws_name}")

        # Data rows span rows 1 .. line_counts[ws_name]-1  (0-indexed)
        data_last_row = line_counts[ws_name] - 1

        chart_num = 0

        if combined_chart:
            chart = workbook.add_chart({'type': chart_type})
            chart.set_size({'width': chart_width, 'height': chart_height * row_height})
            chart.set_legend({'position': legend_position})

            if chart_titles:
                title_cols = '/'.join(labels[pos] for pos in chart_col_pos)
                chart.set_title({'name': f"{ws_name} - {title_cols}"})

            ws.insert_chart((chart_num * chart_height) + 2, 3, chart)

            for col_pos in chart_col_pos:
                col_name = labels[col_pos]
                # xlsxwriter list format: [sheet, first_row, first_col, last_row, last_col]
                series = {
                    'name':       col_name,
                    'categories': [ws_name, 1, category_col_num, data_last_row, category_col_num],
                    'values':     [ws_name, 1, col_pos,          data_last_row, col_pos],
                }
                if col_name == secondary_axis_col:
                    series['y2_axis'] = True
                chart.add_series(series)

        else:
            for col_pos in chart_col_pos:
                col_name = labels[col_pos]
                if debug:
                    print(f"\tCharting column: {col_name}")

                chart = workbook.add_chart({'type': chart_type})
                chart.set_size({'width': chart_width, 'height': chart_height * row_height})
                chart.set_legend({'position': legend_position})

                if chart_titles:
                    chart.set_title({'name': f"{ws_name} - {col_name}"})

                ws.insert_chart((chart_num * chart_height) + 2, 3, chart)

                # xlsxwriter list format: [sheet, first_row, first_col, last_row, last_col]
                chart.add_series({
                    'name':       col_name,
                    'categories': [ws_name, 1, category_col_num, data_last_row, category_col_num],
                    'values':     [ws_name, 1, col_pos,          data_last_row, col_pos],
                })

                chart_num += 1

    # ------------------------------------------------------------------
    # Write the Directory sheet — sorted hyperlinks to every data sheet
    # ------------------------------------------------------------------
    url_format = workbook.add_format({'font_color': 'blue', 'underline': 1})

    for sheet_name in sorted(worksheets.keys()):
        directory.write_url(
            directory_row, 0,
            f"internal:'{sheet_name}'!A1",
            url_format,
            sheet_name,
        )
        directory_row += 1

    workbook.close()


if __name__ == '__main__':
    main()
