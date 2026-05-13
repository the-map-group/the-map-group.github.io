#!/usr/bin/perl

system "ls -d */ > members";

open MEMBERS_FILE, "members" or die "Can't open countries file to read!\n";
my @members_lines = <MEMBERS_FILE>;
close MEMBERS_FILE;

foreach (@members_lines) {
    s/\/\n//;
    system "update-html.sh $_";
    print "updated 'index.html' of country: $_\n"
}

system "rm members"
