#!/usr/bin/python3

# Author: Haraldo Albergaria
# Date  : Jul 29, 2020
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


import flickrapi
import api_credentials
import config
import aliases
import importlib
import json
import time
import os
import sys

#===== CONSTANTS =================================#

api_key = api_credentials.api_key
api_secret = api_credentials.api_secret
user_id = api_credentials.user_id

alias_dict = aliases.alias_dict

group_url = "https://www.flickr.com/groups/the-map-group/"
photos_url = "http://www.flickr.com/photos"
map_group_url = "https://the-map-group.top"

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

# get full script's path
repo_path = os.path.dirname(os.path.realpath(__file__))
people_path = repo_path + "/people"

# open log file
try:
    log_file = open('{}/log/update-maps.log'.format(repo_path), 'a')
except Exception as e:
    print("ERROR: FATAL: Unable to open log file")
    print(str(e))
    sys.exit()

#===== FUNCTIONS ==============================================================#

def getMemberInfo(member_path, repo_path):
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
    member_n_countries = user_info['countries']
    return [member_id, member_alias, member_name, member_avatar, member_n_places, member_n_photos, member_n_countries]


def memberFilesExist(member_path):
    locations_exists = os.path.exists("{}/locations.py".format(member_path))
    coords_exists = os.path.exists("{}/coords.py".format(member_path))
    countries_exists = os.path.exists("{}/countries.py".format(member_path))
    user_exists = os.path.exists("{}/user.py".format(member_path))
    if locations_exists and coords_exists and countries_exists and user_exists:
        return True
    return False

def sendEmail(member_name):
    try:
        os.system("echo \"Member \'" + member_name + "\' has joined the group but has no geotagged photos.\" | mail -s \"The Map Group: New member with no photos\" admin@the-map-group.top")
    except:
        pass


#===== MAIN CODE ==============================================================#

if os.path.exists("{}/success".format(repo_path)):
    os.system("rm {}/success".format(repo_path))

reset_all = config.reset_all
reset_coords = config.reset_coords
force_reset = config.force_reset

try:
    from reset import reset_list
except Exception as e:
    print('ERROR: FATAL: Unable to read reset list file')
    print(str(e))
    log_file.write('ERROR: FATAL: Unable to read reset list file\n')
    log_file.write(str(e))
    sys.exit()

current_members = []
members_list = []

if reset_all and os.path.exists("{}/members.py".format(repo_path)):
    os.system("rm {}/members.py".format(repo_path))

# get group id and name from group url
try:
    group_id = flickr.urls.lookupGroup(api_key=api_key, url=group_url)['group']['id']
    group_name = flickr.groups.getInfo(group_id=group_id)['group']['name']['_content']
except Exception as e:
    print('ERROR: FATAL: Unable to get group information')
    print(str(e))
    log_file.write('ERROR: FATAL: Unable to get group information\n')
    log_file.write(str(e))
    sys.exit()

# get members from group
try:
    members = flickr.groups.members.getList(api_key=api_key, group_id=group_id)
    total_of_members = int(members['members']['total'])
    number_of_pages  = int(members['members']['pages'])
    members_per_page = int(members['members']['perpage'])
except Exception as e:
    print('ERROR: FATAL: Unable to get members list')
    print(str(e))
    log_file.write('ERROR: FATAL: Unable to get members list\n')
    log_file.write(str(e))
    sys.exit()

# iterate over each members page
for page_number in range(number_of_pages, 0, -1):

    try:
        members = flickr.groups.members.getList(api_key=api_key, group_id=group_id, page=page_number, per_page=members_per_page)['members']['member']
    except Exception as e:
        print('ERROR: FATAL: Unable to get members list page')
        print(str(e))
        log_file.write('ERROR: FATAL: Unable to get members list page\n')
        log_file.write(str(e))
        sys.exit()

    members_in_page = len(members)
    if members_in_page > members_per_page:
        members_in_page = members_per_page

    # iterate over each member in page
    for member_number in range(members_in_page-1, -1, -1):

        member_name = members[member_number]['username']
        member_id = members[member_number]['nsid']

        try:
            member_alias = alias_dict[member_id]
        except:
            member_alias = None

        if member_alias == None or member_alias == member_id:
            try:
                member_alias = flickr.people.getInfo(api_key=api_key, user_id=member_id)['person']['path_alias']
            except:
                member_alias = None

            if member_alias == None:
                member_alias = member_id

            alias_dict[member_id] = member_alias

        current_members.append(member_alias)

        member_path = people_path + "/" + member_alias

        if member_alias != member_id and os.path.exists("{}/{}".format(people_path, member_id)):
            if not os.path.exists(member_path):
                os.system("mv {}/{} {}".format(people_path, member_id, member_path))
                os.system("git add {}/*".format(member_path))
                os.system("git rm -fr {}/{}".format(people_path, member_id))
                print('Renamed member directory: {} -> {}'.format(member_id, member_alias))
                log_file.write('Renamed member directory: {} -> {}\n'.format(member_id, member_alias))
            else:
                print('Removed old member directory: {}'.format(member_id))
                log_file.write('Removed old member directory: {}'.format(member_id))

        if (reset_all or member_alias in reset_list) and os.path.exists("{}/last_total.py".format(member_path)):
            if force_reset:
                 os.system("rm {}/last_total.py".format(member_path))
            else:
                print('WARNING: Map has already been generated for member: {}'.format(member_name[0:20]))
                log_file.write('WARNING: Map has already been generated for member: {}\n'.format(member_name[0:20]))

                # get member information
                print("Getting member information...")
                log_file.write("Getting member information...\n")

                member_info = getMemberInfo(member_path, repo_path)
                member_n_places = member_info[4]

                if member_n_places > 0:
                    members_list.append(member_info)

                print("Finished!\n")
                log_file.write("Finished!\n\n")
                continue

        # create member directory and topic if doesn't exist yet
        is_new_member = False
        if not os.path.isdir(member_path):
            command = "{0}/setup-member.sh {1}".format(people_path, member_alias)
            os.system(command)
            is_new_member = True

        if is_new_member:
            print('##### Generating map for new member: {}...'.format(member_name[0:16]))
            log_file.write('##### Generating map for new member: {}...\n'.format(member_name[0:16]))
        else:
            print('##### Updating map for member: {}...'.format(member_name[0:20]))
            log_file.write('##### Updating map for member: {}...\n'.format(member_name[0:20]))

            if not reset_all and not os.path.exists("{}/generate-map-data.py".format(member_path)):
                command = "{0}/restart-member.sh {1}".format(people_path, member_alias)
                os.system(command)

            if reset_all or member_alias in reset_list:
                if not reset_all:
                    print('\'{}\' is in reset list.'.format(member_alias))
                    log_file.write('\'{}\' is in reset list.\n'.format(member_alias))
                if reset_coords and os.path.exists("{}/coords.py".format(member_path)):
                    os.system("rm {}/coords.py".format(member_path))
                if not os.path.exists("{}/coords.py".format(member_path)):
                    print('Resetting member...')
                    log_file.write('Resetting member...\n')
                    command = "{0}/setup-member.sh {1}".format(people_path, member_alias)
                else:
                    print('Restarting member...')
                    log_file.write('Restarting member...\n')
                    command = "{0}/restart-member.sh {1}".format(people_path, member_alias)
                os.system(command)
            else:
                # get 'locations.py', 'countries.py' and 'user.js' from github
                print('Getting locations and countries...')
                log_file.write('Getting locations and countries...\n')
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
                    if not os.path.exists("{}/coords.py".format(member_path)):
                        command = "wget -q -P {0} https://raw.githubusercontent.com/the-map-group/the-map-group.github.io/master/people/{1}/coords.py".format(member_path, member_alias)
                        os.system(command)
                except:
                    pass

            if not reset_all and not memberFilesExist(member_path):
                print('Unable to locate at least one of the member\'s files. Restarting member...')
                log_file.write('Unable to locate at least one of the member\'s files. Restarting member...\n')
                command = "{0}/restart-member.sh {1}".format(people_path, member_alias)
                os.system(command)

        if os.path.exists("{}/locations.py".format(member_path)):
            prev_loc_fsize = os.stat("{}/locations.py".format(member_path)).st_size
        else:
            prev_loc_fsize = 0

        # write member header at log files
        info_htm_file = open("{}/log/index.html".format(repo_path), "a")
        info_log_file = open("{}/log/countries_info.log".format(repo_path), "a")
        info_rep_file = open("{}/log/countries_info.rep".format(repo_path), "a")
        info_err_file = open("{}/log/countries_info.err".format(repo_path), "a")

        info_htm_file.write("<br>##### {}:<br>\n".format(member_name))
        info_log_file.write("\n##### {}:\n".format(member_name))
        info_rep_file.write("\n##### {}:\n".format(member_name))
        info_err_file.write("\n##### {}:\n".format(member_name))

        info_htm_file.close()
        info_log_file.close()
        info_rep_file.close()
        info_err_file.close()

        # generate/update member's map
        print('Starting \'Flickr Map\' script...')
        log_file.write('Starting \'Flickr Map\' script...\n')

        log_file.close()

        command = "{}/generate-map-data.py".format(member_path)
        os.system(command)

        if os.path.exists("{}/fatal".format(member_path)):
            os.system("cp -f {}/fatal {}/fatal".format(member_path, repo_path))

        log_file = open('{}/log/update-maps.log'.format(repo_path), 'a')

        if os.path.exists("{}/locations.py".format(member_path)):
            loc_fsize = os.stat("{}/locations.py".format(member_path)).st_size
            loc_fsize_diff = loc_fsize - prev_loc_fsize
        else:
            loc_fsize_diff = 0

        # commit map
        if memberFilesExist(member_path):
            if reset_all or ((loc_fsize_diff != 0 or (is_new_member and loc_fsize > 21))):
                print('Commiting map data...')
                log_file.write('Commiting map data...\n')
                os.system("git add -f {}/photos/index.html".format(member_path))
                os.system("git add -f {}/index.html".format(member_path))
                os.system("git add -f {}/locations.py".format(member_path))
                os.system("git add -f {}/countries.py".format(member_path))
                os.system("git add -f {}/user.py".format(member_path))
                os.system("git add -f {}/coords.py".format(member_path))
                os.system("git add -f {}/last_total.py".format(member_path))
                os.system("git add -f {}/countries/*".format(repo_path))
                os.system("git add -f {}/not_found.py".format(repo_path))
                os.system("git add -f {}/log/*".format(repo_path))
                os.system("git commit -m \"[auto] Updated map for member \'{}\'\"".format(member_name))
                os.system("git push origin main")
                print('Done!')
                log_file.write('Done!\n')
            else:
                print("Everything is up-to-date. Nothing to commit!")
                log_file.write("Everything is up-to-date. Nothing to commit!\n")
                os.system("git checkout -- {}/".format(member_path))
        else:
            print("ERROR: Missing member files. Aborted.\n")
            log_file.write("ERROR: Missing member files. Aborted.\n\n")
            continue

        # create discussion topic for new member
        if is_new_member and loc_fsize > 21:
            topic_subject = "[MAP] {}".format(member_name)
            member_map = "{0}/people/{1}/".format(map_group_url, member_alias)
            topic_message = "[{0}/{1}/] Your map has been created!\n\nMap link: <a href=\"{3}\"><b>{3}</b></a>\n\nClick on the markers to see the photos taken on the corresponding location.".format(photos_url, member_alias, member_name, member_map)
            flickr.groups.discuss.topics.add(api_key=api_key, group_id=group_id, subject=topic_subject, message=topic_message)
            print('Created discussion topic for new member')
            log_file.write('Created discussion topic for new member\n')

        if loc_fsize <= 21:
            print('Member has no geottaged photos. Sending e-mail...')
            log_file.write('Member has no geottaged photos. Sending e-mail...\n')
            sendEmail(member_name)

        # get member information
        print("Getting member information...")
        log_file.write("Getting member information...\n")

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
        member_n_countries = user_info['countries']

        if member_n_places > 0:
            members_list.append([member_id, member_alias, member_name, member_avatar, member_n_places, member_n_photos, member_n_countries])

        print("Done!\n")
        log_file.write("Done!\n\n")

        os.system("rm -fr {}/__pycache__".format(member_path))

# restore original reset.py file
os.system("git checkout -- {}/reset.py".format(repo_path))

# remove countries members file
if os.path.exists("{}/countries/members.py".format(repo_path)):
    os.system("rm {}/countries/members.py".format(repo_path))

# write new members.py files
members_file = open("{}/members.py".format(repo_path), 'w')
members_file.write("members_list = [\n")

for i in range(len(members_list)):
    members_file.write("  [\'{0}\', \'{1}\', \'{2}\', \"{3}\", {4}, {5}, {6}".format(members_list[i][0], members_list[i][1], members_list[i][2].replace("\'", "\\\'"), members_list[i][3], members_list[i][4], members_list[i][5], members_list[i][6]))
    if i < len(members_list)-1:
        members_file.write("],\n")
    else:
        members_file.write("]\n")

    # updates countries members file
    member_path = people_path + "/" + members_list[i][1]
    if memberFilesExist(member_path):
        command = "{}/update-countries-map-data.py".format(member_path)
        os.system(command)

members_file.write("]\n")
members_file.close()

# write new alias_dict.py file
alias_dict_file = open("{}/aliases.py".format(repo_path), 'w')
alias_dict_file.write("alias_dict = {\n")

for id in alias_dict:
    alias_dict_file.write("  \'{}\': \'{}\',\n".format(id, alias_dict[id]))

alias_dict_file.write("}\n")
alias_dict_file.close()

# update group map
print("##### Updating Group's Map...")
log_file.write("##### Updating Group's Map...\n")

if os.path.exists("{}/last_total.py".format(repo_path)):
    os.system("rm {}/last_total.py".format(repo_path))

log_file.close()

command = "{}/generate-map-data.py".format(repo_path)
os.system(command)

log_file = open('{}/log/update-maps.log'.format(repo_path), 'a')

print('Commiting map data...')
log_file.write('Commiting map data...\n')
os.system("git add -f {}/locations.py".format(repo_path))
os.system("git add -f {}/members.py".format(repo_path))
os.system("git add -f {}/aliases.py".format(repo_path))
os.system("git add -f {}/countries/*".format(repo_path))
os.system("git add -f {}/last_total.py".format(repo_path))
os.system("git add -f {}/not_found.py".format(repo_path))
os.system("git add -f {}/log/*".format(repo_path))
os.system("git commit -m \"[auto] Updated group map\"")
os.system("git push origin main")
print('Done!')
log_file.write('Done!\n')

os.system("rm -fr {}/__pycache__".format(repo_path))

if len(reset_list) > 0:
    os.system("git checkout -- {}/reset.py".format(repo_path))

if not os.path.exists("{}/fatal".format(repo_path)):
    os.system("touch {}/success".format(repo_path))

# check if all members were processed before remove members
if len(current_members) < total_of_members:
    log_file.close()
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

print("\n##### Removing members which have left the group...")
log_file.write("\n##### Removing members which have left the group...\n")

if len(current_members) == len(members_dirs):
    print("No member has left the group!")
    log_file.write("No member has left the group!\n")
    log_file.close()
    os.system("git add -f {}/log/*".format(repo_path))
    os.system("git commit -m \"[auto] Updated log file\"")
    os.system("git push origin main")
    sys.exit()

topics = []

topics_num_of_pages = flickr.groups.discuss.topics.getList(api_key=api_key, group_id=group_id, per_page='500')['topics']['pages']

# iterate over each topics page
for page_number in range(topics_num_of_pages, 0, -1):

    try:
        topics_page = flickr.groups.discuss.topics.getList(api_key=api_key, group_id=group_id, page=page_number, per_page='500')['topics']['topic']
    except Exception as e:
        print('ERROR: FATAL: Unable to get discussion topics')
        print(str(e))
        log_file.write('ERROR: FATAL: Unable to get discussion topics\n')
        log_file.write(str(e))
        log_file.close()
        os.system("git add -f {}/log/*".format(repo_path))
        os.system("git commit -m \"[auto] Updated log file\"")
        os.system("git push origin main")
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
        os.system("rm -fr {0}/{1}".format(people_path, member))
        print("Removed member: {}".format(member))
        log_file.write("Removed member: {}\n".format(member))
        os.system("git add -f {}/log/*".format(repo_path))
        os.system("git commit -m \"[auto] Removed member \'{}\'\"".format(member))
        os.system("git push origin main")
        removed += 1
        for topic in topics:
            if member in topic[1]:
                reply_message = "[https://www.flickr.com/photos/{}/] Your map has been removed. Feel free to come back anytime and a new map will be created for you.".format(member)
                flickr.groups.discuss.replies.add(api_key=api_key, group_id=group_id, topic_id=topic[0], message=reply_message)

log_file.close()
