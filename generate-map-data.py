#!/usr/bin/python3

# This script generates a html file of all the photos on the
# Flickr user's photostream, that can be viewed in a web browser as a map
#
# Author: Haraldo Albergaria
# Date  : Jul 21, 2020
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import flickrapi
import json
import os
import sys
import time
import math

from countries_info import getCountryInfo


# ================= CONFIGURATION VARIABLES =====================

# Limits
photos_per_page = '500'
max_number_of_pages = 10
max_number_of_photos = max_number_of_pages * int(photos_per_page)
max_number_of_markers = 2000


# ===============================================================

# get full script's path
run_path = os.path.dirname(os.path.realpath(__file__))

# open log file
try:
    log_file = open('{}/log/update-maps.log'.format(run_path), 'a')
except Exception as e:
    print("ERROR: FATAL: Unable to open log file")
    print(str(e))
    sys.exit()

# check if there is a api_credentials file and import it
if os.path.exists("{}/api_credentials.py".format(run_path)):
    import api_credentials
else:
    print("ERROR: File 'api_credentials.py' not found. Create one and try again.")
    log_file.write("ERROR: File 'api_credentials.py' not found. Create one and try again.\n")
    sys.exit()

# Credentials
api_key = api_credentials.api_key
api_secret = api_credentials.api_secret

# Flickr api access
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')



#===== MAIN CODE ==============================================================#

# get group id from group url on config file
try:
    group_info = flickr.urls.lookupGroup(api_key=api_key, url='flickr.com/groups/the-map-group/')['group']
    group_id = group_info['id']
    group_name = group_info['groupname']['_content']
except:
    sys.exit()

# stores the coordinates of the markers
coordinates = []

# get the total number of photos
try:
    photos = flickr.groups.pools.getPhotos(api_key=api_key, group_id=group_id, per_page=photos_per_page)
    npages = int(photos['photos']['pages'])
    total = int(photos['photos']['total'])
    print('Generating map for \'{}\''.format(group_name))
    print('{} photos in the pool'.format(total))
    log_file.write('Generating map for \'{}\'\n'.format(group_name))
    log_file.write('{} photos in the pool\n'.format(total))
except Exception as e:
    print('ERROR: FATAL: Unable to get photos from the pool')
    print(str(e))
    log_file.write('ERROR: FATAL: Unable to get photos from the pool\n')
    log_file.write(str(e))
    sys.exit()

# current number of photos on photostream
current_total = total

# difference on number of photos from previous run
delta_total = int(total)

# if there is no difference, finish script
if os.path.exists("{}/last_total.py".format(run_path)):
    import last_total
    delta_total = int(current_total) - int(last_total.number)
    if delta_total == 0:
        print('No changes on number of photos since last run.\nAborted.')
        log_file.write('No changes on number of photos since last run.\nAborted.\n')
        sys.exit()

# if difference > 0, makes total = delta_total
# to process only the new photos, otherwise
# (photos were deleted), run in all
# photostream to update the entire map
if delta_total > 0:
    total = delta_total
    if total != delta_total:
        print('{} new photo(s)'.format(total))
        log_file.write('{} new photo(s)\n'.format(total))
else:
    n_deleted = abs(delta_total)
    if os.path.exists("{}/locations.py".format(run_path)):
        os.system("rm {}/locations.py".format(run_path))
    print('{} photo(s) deleted from photos pool.\nThe corresponding markers will also be deleted'.format(n_deleted))
    log_file.write('{} photo(s) deleted from photos pool.\nThe corresponding markers will also be deleted\n'.format(n_deleted))


print('Extracting photo coordinates and ids...')
log_file.write('Extracting photo coordinates and ids...\n')

# get number of pages to be processed
npages = math.ceil(total/int(photos_per_page))

# to be included on map
n_photos = 0  # counts number of photos
n_markers = 0 # counts number of markers

# extracts only the photos below a number limit
if npages > max_number_of_pages:
    npages = max_number_of_pages
    total = max_number_of_pages * int(photos_per_page);
    print('Extracting for the last {} photos'.format(total))
    log_file.write('Extracting for the last {} photos\n'.format(total))

# process each page
for pg in range(1, npages+1):

    try:
        page = flickr.groups.pools.getPhotos(api_key=api_key, group_id=group_id, privacy_filter='1', extras='geo,tags,url_sq', page=pg, per_page=photos_per_page)['photos']['photo']
    except Exception as e:
        print('ERROR: FATAL: Unable to get photos from the pool')
        print(str(e))
        log_file.write('ERROR: FATAL: Unable to get photos from the pool\n')
        log_file.write(str(e))
        sys.exit()

    photos_in_page = len(page)

    # process each photo on page
    for ph in range(0, photos_in_page):

        photo = page[ph]

        # variable to store information if already exist a marker
        # on the same photo's coordinates
        marker_exists = False

        n_photos += 1

        # get coordinates from photo
        longitude = float(photo['longitude'])
        latitude = float(photo['latitude'])
        photo_owner = photo['owner']

        # read each markers coordinates and append photo is case
        # there is already a marker on the same coordinate
        for coord in coordinates:
            if longitude == coord[0][0] and latitude == coord[0][1]:
                coord[2].append([photo['id'], photo['url_sq']])
                marker_exists = True
                break

        # create a new marker to be added to the map
        if not marker_exists:
            coordinates.append([[longitude, latitude], photo_owner, [[photo['id'], photo['url_sq']]]])
            n_markers += 1

        # stop processing photos if any limit was reached
        if n_photos >= total or n_photos >= max_number_of_photos or n_markers >= max_number_of_markers:
            break

    print('Batch {0}/{1} | {2} photo(s) in {3} marker(s)'.format(pg, npages, n_photos, n_markers), end='\r')
    log_file.write('Batch {0}/{1} | {2} photo(s) in {3} marker(s)\r'.format(pg, npages, n_photos, n_markers))

    # stop processing pages if any limit was reached
    if n_photos >= total:
        break
    if n_photos >= max_number_of_photos:
        print("\nMaximum number of photos on map reached!", end='')
        log_file.write("Maximum number of photos on map reached!\n")
        break
    if n_markers >= max_number_of_markers:
        print("\nMaximum number of markers on map reached!", end='')
        log_file.write("\nMaximum number of markers on map reached!\n")
        break

print('\nAdding marker(s) to map...')
log_file.write('Adding marker(s) to map...\n')

# check if there is a file with the markers on map already
# and import it otherwise created a new variable
locations = []
if os.path.exists("{}/locations.py".format(run_path)):
    try:
        from locations import locations
    except:
        pass

# create a new location file or overwrite existing one
locations_file = open("{}/locations.py".format(run_path), 'w')
locations_file.write("locations = [\n")

# get the number of markers (locations) already on map
n_locations = len(locations)
if n_locations > 0:
    print('Map already has {} marker(s)'.format(n_locations))
    log_file.write('Map already has {} marker(s)\n'.format(n_locations))

# counts the number of new photos added to markers
new_photos = 0

# process each marker info already on map
for loc in range(n_locations):

    # get info for photos on marker
    photos_info = locations[loc][3]
    n_photos = int(locations[loc][4])

    # get number of photos (coordinates) to be added to map
    n_coords = len(coordinates)

    # iterate over each coordinate
    for coord in range(n_coords-1, -1, -1):

        # if there is already a marker on the same coordinate
        if coordinates[coord][0] == locations[loc][0]:

            photo_owner = locations[loc][1]

            # read each photo already on the marker
            for photo in coordinates[coord][2]:
                photo_id = photo[0]
                thumb_url = photo[1]

                # if the photo is not already on marker, add the photo to it
                if [photo_id, thumb_url] not in photos_info:
                    photos_info.append([photo_id, thumb_url])
                    new_photos += 1

            # remove photo info from
            # coordinates to be added
            coordinates.pop(coord)

    # update the number of photos on marker
    locations[loc][3] = photos_info
    locations[loc][4] = len(photos_info)
    locations_file.write("    {}".format(locations[loc]))

    if len(coordinates) > 0:
        locations_file.write(",\n")
    else:
        locations_file.write("\n")


if new_photos > 0:
    print('Added {} new photo(s) to existing markers'.format(new_photos))
    log_file.write('Added {} new photo(s) to existing markers\n'.format(new_photos))

# reverse the coordinates order so
# the newest ones go to the end
coordinates.reverse()

# check if there is remaining markers to be added
n_markers = len(coordinates)
if n_markers > 0:
    print('{} new marker(s) will be added to the map'.format(n_markers))
    log_file.write('{} new marker(s) will be added to the map\n'.format(n_markers))

# remove the oldest locations to make
# room for new markers without violate
# the max number of markers limit
new_locations_length = len(locations) + n_markers
if new_locations_length >= max_number_of_markers:
    new_locations_length = max_number_of_markers - n_markers
    print('Max number of markers reached. Removing {} marker(s)...'.format(n_markers))
    log_file.write('Max number of markers reached. Removing {} marker(s)...\n'.format(n_markers))
    while len(locations) > new_locations_length:
        locations.pop(0)

new_markers = 0

# iterate over each marker to be added
for marker_info in coordinates:

    new_markers += 1

    # get coordinates of the new marker
    longitude = float(marker_info[0][0])
    latitude = float(marker_info[0][1])
    photo_owner = marker_info[1]
    try:
        country_info = getCountryInfo(latitude, longitude, dict())
        country_code = country_info[0]
        country_name = country_info[1]
    except:
        country_code = ''
        country_name = ''

    # write it to locations file
    locations_file.write("    [[{0}, {1}], \'{2}\', \'{3}\', [".format(longitude, latitude, country_code, photo_owner))

    # counts the number of photos
    n_photos = 0

    # iterate over each photo
    for photo in marker_info[2]:

        # add photo to marker, writing it to locations file
        locations_file.write("[\'{0}\', \'{1}\']".format(photo[0], photo[1]))
        n_photos += 1

        if n_photos < len(marker_info[2]):
            locations_file.write(", ")

    # finish marker writing to location file
    locations_file.write("], {}]".format(n_photos))
    if new_markers < n_markers:
        locations_file.write(",\n")
    else:
        locations_file.write("\n")

    print('Added marker {0}/{1}'.format(new_markers, n_markers), end='\r')
    log_file.write('Added marker {0}/{1}\r'.format(new_markers, n_markers))

# finish script
if new_markers > 0:
    print('')
    log_file.write('\n')
else:
    print('No new markers were added to the map')
    log_file.write('No new markers were added to the map\n')

print('Finished!')
log_file.write('Finished!\n')

locations_file.write("]\n")
locations_file.close()

# update last_total file with the new value
if os.path.exists("{}/locations.py".format(run_path)):
    os.system("echo \"number = {0}\" > {1}/last_total.py".format(current_total, run_path))

log_file.close()
