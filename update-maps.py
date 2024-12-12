#!/usr/bin/python3

# Author: Haraldo Albergaria
# Date  : Jul 29, 2020
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


import flickrapi
import api_credentials
import importlib
import json
import time
import os
import sys


#===== CONSTANTS =================================#

api_key = api_credentials.api_key
api_secret = api_credentials.api_secret
user_id = api_credentials.user_id

group_url = "https://www.flickr.com/groups/the-map-group/"
photos_url = "http://www.flickr.com/photos"
map_group_url = "https://the-map-group.top"

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

# get full script's path
repo_path = os.path.dirname(os.path.realpath(__file__))
people_path = repo_path + "/people"


#===== FUNCTIONS ==============================================================#

def memberFilesExist(member_path):
    locations_exists = os.path.exists("{}/locations.py".format(member_path))
    countries_exists = os.path.exists("{}/countries.py".format(member_path))
    user_exists = os.path.exists("{}/user.py".format(member_path))
    if locations_exists and countries_exists and user_exists:
        return True
    return False

def sendEmail(member_name):
    try:
        os.system("echo \"Member \'" + member_name + "\' has joined the group but has no geotagged photos.\" | mail -s \"The Map Group: New member with no photos\" admin@the-map-group.top")
    except:
        pass


#===== MAIN CODE ==============================================================#

reset = True

if reset:
    command = "rm {}/countries/members.py".format(repo_path)
    os.system(command)

current_members = []
members_list = []

# get group id and name from group url
try:
    group_id = flickr.urls.lookupGroup(api_key=api_key, url=group_url)['group']['id']
    group_name = flickr.groups.getInfo(group_id=group_id)['group']['name']['_content']
except:
    sys.exit()

# get members from group
try:
    members = flickr.groups.members.getList(api_key=api_key, group_id=group_id)
    total_of_members = int(members['members']['total'])
    number_of_pages  = int(members['members']['pages'])
    members_per_page = int(members['members']['perpage'])
except:
    sys.exit()

if os.path.exists("{}/countries/members.py".format(repo_path)):
    os.system("rm {}/countries/members.py".format(repo_path))

# iterate over each members page
for page_number in range(number_of_pages, 0, -1):

    try:
        members = flickr.groups.members.getList(api_key=api_key, group_id=group_id, page=page_number, per_page=members_per_page)['members']['member']
    except:
        sys.exit()

    members_in_page = len(members)
    if members_in_page > members_per_page:
        members_in_page = members_per_page

    # iterate over each member in page
    for member_number in range(members_in_page-1, -1, -1):
        try:
            member_name = members[member_number]['username']
            member_id = members[member_number]['nsid']
            member_alias = flickr.people.getInfo(api_key=api_key, user_id=member_id)['person']['path_alias']
            if member_alias == None:
                member_alias = member_id
            member_path = people_path + "/" + member_alias

            current_members.append(member_alias)

            # create member directory and topic if doesn't exist yet
            is_new_member = False
            if not os.path.isdir(member_path):
                command = "{0}/setup-member.sh {1}".format(people_path, member_alias)
                os.system(command)
                is_new_member = True

            if is_new_member:
                print('##### Generating map for new member: {}...'.format(member_name[0:16]))
            else:
                print('##### Updating map for member: {}...'.format(member_name[0:20]))

                if not reset:
                    # get 'locations.py', 'countries.py' and 'user.js' from github
                    print('Getting locations and countries from remote...')
                    try:
                        if not os.path.exists("{}/locations.py".format(member_path)):
                            command = "wget -q -P {0} https://raw.githubusercontent.com/the-map-group/the-map-group.github.io/master/people/{1}/locations.py".format(member_path, member_alias)
                            os.system(command)
                        if not os.path.exists("{}/countries.py".format(member_path)):
                            command = "wget -q -P {0} https://raw.githubusercontent.com/the-map-group/the-map-group.github.io/master/people/{1}/countries.py".format(member_path, member_alias)
                            os.system(command)
                        if not os.path.exists("{}/user.py".format(member_path)):
                            command = "wget -q -P {0} https://raw.githubusercontent.com/the-map-group/the-map-group.github.io/master/people/{1}/user.py".format(member_path, member_alias)
                            os.system(command)
                    except:
                        pass

            if not reset and not is_new_member and not memberFilesExist(member_path):
                continue

            if memberFilesExist(member_path):
                prev_loc_fsize = os.stat("{}/locations.py".format(member_path)).st_size
            else:
                prev_loc_fsize = 0

            # generate/update member's map
            print('Starting \'Flickr Map\' script...')
            command = "{}/generate-map-data.py".format(member_path)
            os.system(command)

            if memberFilesExist(member_path):
                loc_fsize = os.stat("{}/locations.py".format(member_path)).st_size
                loc_fsize_diff = loc_fsize - prev_loc_fsize
            else:
                loc_fsize_diff = 0

            # updates countries members file
            if memberFilesExist(member_path):
                command = "{}/update-countries-map-data.py".format(member_path)
                os.system(command)

            # commit map
            if reset or ((loc_fsize_diff != 0 or (is_new_member and loc_fsize > 21)) and memberFilesExist(member_path)):
                print('Commiting map data...')
                os.system("git add -f {}/index.html".format(member_path))
                os.system("git add -f {}/locations.py".format(member_path))
                os.system("git add -f {}/countries.py".format(member_path))
                os.system("git add -f {}/user.py".format(member_path))
                os.system("git add -f {}/not_found_places.py".format(repo_path))
                os.system("git add -f {}/log/*".format(repo_path))
                os.system("git commit -m \"[auto] Updated map for member \'{}\'\"".format(member_name))
                os.system("git push origin main")
                print('Done!')
            else:
                print("Everything is up-to-date. Nothing to commit!")

            # create discussion topic for new member
            if is_new_member and loc_fsize > 21:
                topic_subject = "[MAP] {}".format(member_name)
                member_map = "{0}/people/{1}/".format(map_group_url, member_alias)
                topic_message = "[{0}/{1}/] Your map has been created! If you can not see it yet, please, wait some minutes and try again.\n\nMap link: <a href=\"{3}\"><b>{3}</b></a>\n\nClick on the markers to see the photos taken on the corresponding location.".format(photos_url, member_alias, member_name, member_map)
                flickr.groups.discuss.topics.add(api_key=api_key, group_id=group_id, subject=topic_subject, message=topic_message)
                print('Created discussion topic for new member')

            if loc_fsize <= 21:
                print('Member has no geottaged photos. Sending e-mail...')
                sendEmail(member_name)

        except:
            pass

        if not os.path.exists("{}/user.py".format(member_path)):
            continue

        # get member information
        print("Getting member information...")

        os.system("cp {0}/user.py {1}/".format(member_path, repo_path))
        import user
        importlib.reload(user)
        from user import user_info
        os.system("rm {}/user.py".format(repo_path))

        member_name = user_info['name']
        if len(member_name) > 30:
            member_name = member_name[:30]

        member_avatar = "{}".format(user_info['avatar'].replace('../../', ''))

        member_n_places = user_info['markers']
        member_n_photos = user_info['photos']

        already_in_list = False
        for i in range(len(members_list)):
            if members_list[i][0] == member_id:
                members_list[i][4] = member_n_places
                members_list[i][5] = member_n_photos
                already_in_list = True

        if not already_in_list and member_n_places > 0:
            members_list.append([member_id, member_alias, member_name, member_avatar, member_n_places, member_n_photos])

        print("Finished!\n")

        if os.path.exists("{}/locations.py".format(member_path)):
            os.system("rm {}/locations.py".format(member_path))
        if os.path.exists("{}/countries.py".format(member_path)):
            os.system("rm {}/countries.py".format(member_path))
        if os.path.exists("{}/user.py".format(member_path)):
            os.system("rm {}/user.py".format(member_path))
        os.system("rm -fr {}/__pycache__".format(member_path))

# remove from the list members who left the group
for i in range(len(members_list)-1, -1, -1):
    if members_list[i][1] not in current_members:
        members_list.pop(i)

members_file = open("{}/members.py".format(repo_path), 'w')
members_file.write("members_list = [\n")

for i in range(len(members_list)):
    members_file.write("  [\'{0}\', \'{1}\', \'{2}\', \"{3}\", {4}, {5}".format(members_list[i][0], members_list[i][1], members_list[i][2].replace("\'", "\\\'"), members_list[i][3], members_list[i][4], members_list[i][5]))
    if i < len(members_list)-1:
        members_file.write("],\n")
    else:
        members_file.write("]\n")

members_file.write("]\n")
members_file.close()

# update group map
print("##### Updating Group's Map...")

if os.path.exists("{}/last_total.py".format(repo_path)):
    os.system("rm {}/last_total.py".format(repo_path))

command = "{}/generate-map-data.py".format(repo_path)
os.system(command)

print('Commiting map data...')
os.system("git add -f {}/locations.py".format(repo_path))
os.system("git add -f {}/members.py".format(repo_path))
os.system("git add -f {}/countries/*".format(repo_path))
os.system("git add -f {}/log/*".format(repo_path))
os.system("git commit -m \"[auto] Updated group map\"")
print('Done!')

os.system("rm {}/locations.py".format(repo_path))
os.system("rm {}/members.py".format(repo_path))
os.system("rm -fr {}/__pycache__".format(repo_path))

# check if all members were processed before remove members
if len(current_members) < total_of_members:
    sys.exit()

# get member directories list
os.system("ls -d {0}/*/ > {0}/dirs".format(people_path))
if os.path.exists("{}/dirs".format(people_path)):
    members_dirs_file = open("{}/dirs".format(people_path))
    members_dirs_file_lines = members_dirs_file.readlines()
    os.system("rm {}/dirs".format(people_path))
    members_dirs = []
    for member in members_dirs_file_lines:
        members_dirs.append(member.replace(people_path, '').replace('/', '').replace('\n',''))

if len(current_members) == len(members_dirs):
    print("\nNo member has left the group!")
    sys.exit()

print("\n##### Removing members which have left the group...")

topics = []

topics_num_of_pages = flickr.groups.discuss.topics.getList(api_key=api_key, group_id=group_id, per_page='500')['topics']['pages']

# iterate over each topics page
for page_number in range(topics_num_of_pages, 0, -1):

    try:
        topics_page = flickr.groups.discuss.topics.getList(api_key=api_key, group_id=group_id, page=page_number, per_page='500')['topics']['topic']
    except:
        sys.exit()

    # iterate over each member in page
    for topic in topics_page:
        topics.append([topic['id'], topic['message']['_content']])

# for each member directory check if member has left the group
removed = 0
for member in members_dirs:
    if member not in current_members:
        # remove member directory
        os.system("git rm -fr {0}/{1}".format(people_path, member))
        os.system("git commit -m \"[auto] Removed member \'{}\'\"".format(member))
        os.system("rm -fr {0}/{1}".format(people_path, member))
        print("Removed member: {}".format(member))
        removed += 1
        for topic in topics:
            if member in topic[1]:
                reply_message = "[https://www.flickr.com/photos/{}/] Your map has been removed. Feel free to come back anytime and a new map will be created for you.".format(member)
                flickr.groups.discuss.replies.add(api_key=api_key, group_id=group_id, topic_id=topic[0], message=reply_message)
