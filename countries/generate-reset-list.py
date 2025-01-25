#!/usr/bin/python3

import os
import sys
from members import members_dict

countries_codes = ['AR', 'BR', 'PY']

members_list = []
for code in countries_codes:
    for member in members_dict[code]:
        member_alias = member[1]
        if member_alias not in members_list:
            members_list.append(member_alias)

reset_file = open('reset.py', 'w')
reset_file.write("reset_list = [\n")
for member in members_list:
    reset_file.write("  \'{}\',\n".format(member))
reset_file.write("]\n")
reset_file.close()
