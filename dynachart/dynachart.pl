#!/usr/bin/env perl

# dynachart.pl
# Jared Still 2017-07-23
# still@pythian.com jkstill@gmail.com

# data is from STDIN

use warnings;
use strict;
use Data::Dumper;
use Pod::Usage;
use Getopt::Long;
use Excel::Writer::XLSX;

my $debug = 0;
my $combinedChart = 0;
my %optctl = ();
my ($help,$man);
my @chartCols;
my $categoryColName='';
my $categoryColNum=0;

Getopt::Long::GetOptions(
	\%optctl, 
	'spreadsheet-file=s',
	'debug!' => \$debug,
	'chart-cols=s{1,10}' => \@chartCols,
	'combined-chart!' => \$combinedChart,
	'worksheet-col=s',  # creates a separate worksheet per value of this column
	'category-col=s' => \$categoryColName,
	'h|help|?' => \$help, man => \$man
) or pod2usage(2) ;

pod2usage(1) if $help;
pod2usage(-verbose => 2) if $man;

my $xlFile = defined($optctl{'spreadsheet-file'}) ? $optctl{'spreadsheet-file'} : 'asm-metrics.xlsx';
my $workSheetCol = defined($optctl{'worksheet-col'}) ? $optctl{'worksheet-col'} : 0;

my %fonts = (
	fixed			=> 'Courier New',
	fixed_bold	=> 'Courier New',
	text			=> 'Arial',
	text_bold	=> 'Arial',
);

my %fontSizes = (
	fixed			=> 10,
	fixed_bold	=> 10,
	text			=> 10,
	text_bold	=> 10,
);

my $maxColWidth = 50;
my $counter = 0;
my $interval = 100;

# create workbook
my $workBook = Excel::Writer::XLSX->new($xlFile);
die "Problems creating new Excel file $xlFile: $!\n" unless defined $workBook;

# create formats
my $stdFormat = $workBook->add_format(bold => 0,font => $fonts{fixed}, size => $fontSizes{fixed}, color => 'black');
my $boldFormat = $workBook->add_format(bold => 1,font => $fonts{fixed_bold}, size => $fontSizes{fixed_bold}, color => 'black');
my $wrapFormat = $workBook->add_format(bold => 0,font => $fonts{text}, size => $fontSizes{text}, color => 'black');
$wrapFormat->set_align('vjustify');


my $labels=<>;
chomp $labels;
# sadf starts header lines with '# ' - remove that
$labels =~ s/^#\s+//;
my @labels = split(/,\s*/,$labels);

if ($debug) {

print qq{LABELS:\n};

print join("\n",@labels);

print "\n";

}

# get the X series category
if ( $categoryColName ) {

	my $want = $categoryColName;
	my $index = 0;
	++$index until ($labels[$index] eq $want) or ($index > $#labels);
	$categoryColNum = $index;	

}

#print join("\n",@labels);

# get the element number of the column used to segregate into worksheets
my $workSheetColPos;
if ($workSheetCol) {
	my $i=0;
	foreach my $label ( @labels)  {
		if ($label eq $workSheetCol) { 
			$workSheetColPos = $i;
			last;
		}
		$i++;
	}
}

print "\nworkSheetColPos: $workSheetColPos\n" if $debug;

# validate the columns to be charted
# use as an index into the labels
my @chartColPos=();
{
	my $i=0;
	foreach my $label ( @labels)  {
		foreach my $chartCol ( @chartCols ) {
			if ($label eq $chartCol) { 
				push @chartColPos, $i;
				last;
			}
		}
		$i++;
	}
}

if ($debug) {
	print "\nChartCols:\n", Dumper(\@chartCols);
	print "\nChartColPos:\n", Dumper(\@chartColPos);
	print "\nLabels:\n", Dumper(\@labels);
}

my %lineCount=();
my %workSheets=();


# the first worksheet is a directory
my $directoryName='Directory';
my $directory;
my $noDirectory=0;
my $directoryLineCount=0;

unless ($noDirectory) {
	$directory = $workBook->add_worksheet($directoryName)	;
	$directory->set_column(0,0,30);
	$directory->write_row($directoryLineCount++,0,['Directory'],$boldFormat);
}

while (<>) {

	chomp;
	my @data=split(/,/);

	my $currWorkSheetName;
	if ($workSheetCol) {
		$currWorkSheetName=$data[$workSheetColPos];
		if (length($currWorkSheetName) > 31 ) {
			# cut some out of the middle of the name as the Excel worksheet name has max size of 31
			$currWorkSheetName = substr($currWorkSheetName,0,14) . '...' . substr($currWorkSheetName,-14);
		}
	} else {
		$currWorkSheetName='DynaChart';
	}

	print "Worksheet Name: $currWorkSheetName\n" if $debug;

	unless (defined $workSheets{$currWorkSheetName}) {
		$workSheets{$currWorkSheetName} = $workBook->add_worksheet($currWorkSheetName);
		$workSheets{$currWorkSheetName}->write_row($lineCount{$currWorkSheetName}++,0,\@labels,$boldFormat);
		# freeze pane at header
		$workSheets{$currWorkSheetName}->freeze_panes($lineCount{$currWorkSheetName},0);
	}

	# setup column widths
	#$workSheet->set_column($el,$el,$colWidth);
	$workSheets{$currWorkSheetName}->write_row($lineCount{$currWorkSheetName}++,0,\@data, $stdFormat);

}

if ($debug) {
	print "Worksheets:\n";
	print "$_\n" foreach keys %workSheets;
	print Dumper(\%lineCount);
}

# each row consumes about 18 pixels
my $rowHeight=18; # pixels
my $chartHeight=23; # rows

# triple from default width of 480
my $chartWidth = 480 * 3;

=head1 Write the Charts

 The default mode is to create a separate chart for each metric
 By specifying the command line option --combined-chart the values will be charted in a single chart
 Doing so is probably useful only for a limited number of sets of values

 Some may question the apparent duplication of code in the sections to combine or not combine the charts
 Doing so would be a bit convoluted - this is easier to read and modify

=cut

foreach my $workSheet ( keys %workSheets ) {
	print "Charting worksheet: $workSheet\n" if $debug;

	my $chartNum = 0;

	if ($combinedChart) {
		my $chart = $workBook->add_chart( type => 'line', name => "Combined" . '-' . $workSheets{$workSheet}->get_name(), embedded => 1 );
		$chart->set_size( width => $chartWidth, height => $chartHeight * $rowHeight);
		
		# each chart consumes about 16 rows
		$workSheets{$workSheet}->insert_chart((($chartNum * $chartHeight) + 2),3, $chart);

		foreach my $colPos ( @chartColPos ) {
			my $col2Chart=$labels[$colPos];
			# [ sheet, row_start, row_end, col_start, col_end]
			$chart->add_series(
				name => $col2Chart,
				#categories => [$workSheet, 1,$lineCount{$workSheet},2,2],
				categories => [$workSheet, 1,$lineCount{$workSheet},$categoryColNum,$categoryColNum],
				values => [$workSheet, 1,$lineCount{$workSheet},$colPos,$colPos]
			);
		}
		
	} else {
		foreach my $colPos ( @chartColPos ) {
			my $col2Chart=$labels[$colPos];
			print "\tCharting column: $col2Chart\n" if $debug;
			my $chart = $workBook->add_chart( type => 'line', name => "$col2Chart" . '-' . $workSheets{$workSheet}->get_name(), embedded => 1 );
			$chart->set_size( width => $chartWidth, height => $chartHeight * $rowHeight);

			# each chart consumes about 16 rows
			$workSheets{$workSheet}->insert_chart((($chartNum * $chartHeight) + 2),3, $chart);
		

			# [ sheet, row_start, row_end, col_start, col_end]
			$chart->add_series(
				name => $col2Chart,
				#categories => [$workSheet, 1,$lineCount{$workSheet},2,2],
				categories => [$workSheet, 1,$lineCount{$workSheet},$categoryColNum,$categoryColNum],
				values => [$workSheet, 1,$lineCount{$workSheet},$colPos,$colPos]
			);

			$chartNum++;
		}
	}
}


# write the directory page
my $urlFormat = $workBook->add_format( color => 'blue', underline => 1 );
my %sheetNames=();

foreach my $worksheet ( $workBook->sheets() ) {
	my $sheetName = $worksheet->get_name();
	next if $sheetName eq $directoryName;
	$sheetNames{$sheetName} = $worksheet;
}

foreach my $sheetName ( sort keys %sheetNames ) {
	$directory->write_url($directoryLineCount++,0, qq{internal:'$sheetName'!A1} ,$urlFormat, $sheetName);
}

__END__

=head1 NAME

dynachart.pl

  --help brief help message
  --man  full documentation
  --spreadsheet-file output file name - defaults to asm-metrics.xlsx
  --worksheet-col name of column used to segragate data into worksheets 
    defaults to a single worksheet if not supplied
  --chart-cols list of columns to chart

 dynachart.pl accepts input from STDIN

 This script will read CSV data created by asm-metrics-collector.pl or asm-metrics-aggregator.pl


=head1 SYNOPSIS

dynachart.pl [options] [file ...]

 Options:
   --help brief help message
   --man  full documentation
   --spreadsheet-file output file name - defaults to asm-metrics.xlsx
   --worksheet-col name of column used to segragate data into worksheets 
     defaults to a single worksheet if not supplied
  --chart-cols list of columns to chart
  --category-col specify the column for the X vector - a timestamp is typically used 
    the name must exactly match that in the header
  --combined-chart create a single chart rather than a chart for each value specified in --chart-cols

 dynachart.pl accepts input from STDIN

 dynachart.pl --worksheet-col DISKGROUP_NAME < my_input_file.csv


 dynachart.pl --spreadsheet-file sar-disk-test.xlsx --combined-chart --worksheet-col DEV --category-col 'timestamp' --chart-cols 'rd_sec/s' --chart-cols 'wr_sec/s' < sar-disk-test.csv


=head1 OPTIONS

=over 8

=item B<-help>

Print a brief help message and exits.

=item B<-man>

Prints the manual page and exits.

=item B<--spreadsheet-file>

 The name of the Excel file to create.
 The default name is asm-metrics.xlsx

=item B<--worksheet-col>

 By default a single worksheet is created.
 When this option is used the column supplied as an argument will be used to segragate data into separate worksheets.

=item B<--chart-cols>

 List of columns to chart
 This should be the last option on the command line if used.

 It may be necessary to tell Getopt to stop processing arguments with '--' in some cases.

 eg.

 dynachart.pl dynachart.pl --worksheet-col DISKGROUP_NAME --chart-cols READS WRITES -- logs/asm-oravm-20150512_01-agg-dg.csv

=item B<--category-col>

 Column to use as the category for the X line in the chart - default to the first column
 The name must exactly match a column from the CSV file
 Typically this line is a timestamp

=back

=head1 DESCRIPTION

B<dynachart.pl> creates an excel file with charts for selected columns>

=head1 EXAMPLES

 dynachart.pl accepts data from STDIN
 
 dynachart.pl --worksheet-col DISKGROUP_NAME --spreadsheet-file mywork.xlsx

=cut


