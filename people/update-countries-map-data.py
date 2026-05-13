#!/usr/bin/python3

# Author: Haraldo Albergaria
# Date  : Jul 29, 2020
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys

repo_path = "/home/pi/github/the-map-group.github.io"
countries_path = "{}/countries".format(repo_path)
members = "{}/members.py".format(countries_path)

# write to countries members file
if os.path.exists("{}/members.py".format(countries_path)):
    from countries_members import members_dict
else:
    members_dict = dict()

members_file = open("{}/members.py".format(countries_path), 'w')
members_file.write("members_dict = {\n")

from countries import countries_dict
from user import user_info

for country_code in countries_dict:
    if country_code in members_dict:
        members_dict[country_code].append([user_info['id'], user_info['alias'], user_info['name'], user_info['avatar'], countries_dict[country_code][1], countries_dict[country_code][2]])
    else:
        members_dict[country_code] = [[user_info['id'], user_info['alias'], user_info['name'], user_info['avatar'], countries_dict[country_code][1], countries_dict[country_code][2]]]

i = 0
for country_code in members_dict:

    members_file.write("  \'{0}\': {1}".format(country_code, members_dict[country_code]))
    if i < len(members_dict)-1:
        members_file.write(",\n")
    else:
        members_file.write("\n")
    i += 1

    country_path = "{0}/{1}".format(countries_path, country_code.lower())
    if not os.path.exists("{}/index.html".format(country_path)):
        os.system("mkdir {}".format(country_path))
        os.system("ln -P {0}/index.html {1}/index.html".format(countries_path, country_path))
        country_js_file = open("{}/country_code.js".format(country_path), 'w')
        country_js_file.write("var country_code = \'{}\'\n".format(country_code))
        country_js_file.close()

members_file.write("}\n")
members_file.close()

