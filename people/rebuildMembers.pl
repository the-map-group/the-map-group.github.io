#!/usr/bin/perl

print "This will rebuild all members. Continue? (Yes/No)\n";
my $input = <STDIN>;
chomp $input;

if ($input ne "Yes") {
    exit;
}

print "Rebuilding members...\n";

system "ls -d */ > members";

open MEMBERS_FILE, "members" or die "Can't open members file to read!\n";
my @members_lines = <MEMBERS_FILE>;
close MEMBERS_FILE;

foreach (@members_lines) {
    s/\/\n//;
    system "rebuild-member.sh $_";
    print "rebuilded member: $_\n";
}

system "rm members";
