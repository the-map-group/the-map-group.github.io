#!/bin/bash

REPO_DIR="/storage/emulated/0/GitRepos/github/the-map-group.github.io"
GEN_MAP_DIR="/storage/emulated/0/GitRepos/flickr_map"

if [ -z $1 ];
  then
    echo "Usage: ./setup-member.mob.sh <member>"
    exit 1
fi


if [[ -e $REPO_DIR/people/$1 ]];
    then
        rm -fr $REPO_DIR/people/$1
fi

mkdir $REPO_DIR/people/$1
cd $REPO_DIR/people/$1
cp ../../api_credentials.py .
cp ../../countries_config.py .
cp ../../countries_info.py .
cp ../../log/update-maps.log map.log
cp ../../matrix.py .
cp ../../not_found.py .
cp ../../countries/members.py countries_members.py
cp $GEN_MAP_DIR/generate-map-data.py .
cp ../index.html .
cp ../update-countries-map-data.mob.py update-countries-map-data.py
echo "user = '$1'" > config.py
echo "photoset_id = ''" >> config.py
echo "photo_privacy = 1" >> config.py
echo "geo_privacy = 1" >> config.py
echo "dont_map_tag = 'DontMap'" >> config.py
echo "coords_dict = {" > coords.py
echo "}" >> coords.py
mkdir $REPO_DIR/people/$1/photos
cd $REPO_DIR/people/$1/photos
cp ../../photos.html index.html
