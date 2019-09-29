#!/usr/bin/env perl
#
use strict;
use warnings;
use IO::File;
use Getopt::Long;

# simpler method of assigning defaults with Getopt::Long

my $useHeader=1;
my $hasHeader=1;
my @csvFiles=();
my $delimiter=',';
my $help=0;

GetOptions (
		"csv-file=s" => \@csvFiles,
		"has-header!" => \$hasHeader,
		"use-header!" => \$useHeader,
		"delimiter=s" => \$delimiter,
		"h|help!" => \$help,
) or die usage(1);

usage() if $help;

my $previousFile=$csvFiles[0];
my $retrievedHeader=0;
my $savedHeader=0;
my @headers;
my $maxColNum=0;

if (@csvFiles) {
	foreach my $file (@csvFiles) {
		#print "file: $file\n";
		unless (-r $file) { 
			warn "\nFile $file Not Found!\n";
			usage(2);
		}

		my $fh = IO::File->new;
		$fh->open($file,'<',) || die "could not open $file - $!\n";
		my $line=<$fh>;
		@headers=split(/$delimiter/,$line);

		if ($maxColNum) {
			my $testMaxColNum=$#headers;
			if ($testMaxColNum != $maxColNum ) {
				die "Column Count Mismatch in $file\n"
			}
		} else {
			$maxColNum=$#headers;
		}
}
} else {
	usage(1);
}


if ( ! $hasHeader ){ $useHeader=0 }

foreach my $file ( @csvFiles ) {

	if ($previousFile ne $file) {
		$previousFile = $file;
		$retrievedHeader=0;
	}

	my $fh = IO::File->new;
	$fh->open($file,'<',) || die "could not open $file - $!\n";

	while ( my $line = <$fh> ) {

		# first line of first file
		if ( ! $retrievedHeader ) {
			
			$retrievedHeader=1;
			if (! $savedHeader ) {
				@headers=split(/$delimiter/,$line);
				print $line if $useHeader;
				$savedHeader=1;
			}
			next;
		} 

		print $line;
	}


}

sub usage {

	my $exitVal = shift;
	use File::Basename;
	my $basename = basename($0);
	print qq{
$basename



usage: $basename - combine CSV files into a single file

   $basename --has-header --use-header --csv-file file-1 --csv-file file-2

--csv-file     Formatted length of operation lines - defaults to 80
--has-header   Indicates that the first line of each file is header column names.
               Default is that headers are present
               Use --no-has-header to negate
--use-header   Indicate the output should include a header. Dev
--delimiter    Specify the field delimiter.  Default is a comma

examples here:

   $basename --csv-file file-1.csv --csv-file file-2.csv --no-has-header
};

	exit eval { defined($exitVal) ? $exitVal : 0 };
}

