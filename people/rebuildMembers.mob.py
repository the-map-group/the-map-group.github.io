#!/usr/bin/python3

import os

members_file = open("members_list", "r")

file_lines = members_file.readlines()

for member in file_lines:
	os.system("./rebuild-member.mob.sh {}".format(member.replace("\n", "")))
	print("Rebuilt {}".format(member.replace("\n", "")))

members_file.close()
