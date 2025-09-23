#!/usr/bin/perl

system "ls -d */ > dirs";

open DIRS_FILE, "dirs" or die "Can't open members file to read!\n";
my @dirs_lines = <DIRS_FILE>;
close DIRS_FILE;

open MEMBERS_FILE, "members_list" or die "Can't open members file to read!\n";
my @members_lines = <MEMBERS_FILE>;
close MEMBERS_FILE;

my $is_member;

print "\n#### Removing members which have left the group...\n";
foreach (@dirs_lines) {
    s/\/\n//;
    chomp($_);
    $is_member = 0;
    for (my $i = 0; $i < @members_lines; $i++) {
        $member = @members_lines[$i];
        chomp($member);
        if ($_ eq $member) {
            $is_member = 1;
            last;
        }    
    }
    if ($is_member == 0) {
        #system "git rm -fr $_";
        system "rm -fr $_";
        print "Removed member: $_\n";
    }
}

system "rm dirs";
