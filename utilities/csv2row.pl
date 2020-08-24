#!/usr/bin/env perl

use strict;
use warnings;

while (<STDIN>) {
	chomp;
	my @a=split(",",$_);
	foreach my $el ( 0 .. $#a ) {
		print $el+1 . ': ' . $a[$el] . "\n";
	}
}

