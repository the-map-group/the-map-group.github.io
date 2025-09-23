#!/bin/bash

REPO_DIR="/storage/emulated/0/GitRepos/github/the-map-group.github.io"
GEN_MAP_DIR="/storage/emulated/0/GitRepos/flickr_map"

if [ -z $1 ];
  then
    echo "Usage: ./mob_rebuild-member.sh <member>"
    exit 1
fi

cd $REPO_DIR/people/$1

if [[ ! -e api_credentials.py ]];
  then
    cp ../../api_credentials.py .
fi

if [[ ! -e countries_info.py ]];
  then
    cp ../../countries_info.py .
fi

if [[ ! -e countries_config.py ]];
  then
    cp ../../config.py countries_config.py
fi

if [[ ! -e matrix.py ]];
  then
    cp ../../matrix.py .
fi

if [[ ! -e map.log ]];
  then
    cp ../../log/update-maps.log map.log
fi

if [[ ! -e not_found.py ]];
  then
    cp ../../not_found.py .
fi

if [[ ! -e countries_members.py ]];
  then
    cp ../../countries/members.py countries_members.py
fi

if [[ ! -e generate-map-data.py ]];
  then
    cp $GEN_MAP_DIR/generate-map-data.py .
fi

if [[ ! -e index.html ]];
  then
    cp ../index.html .
fi

if [[ ! -e update-countries-map-data.py ]];
  then
    cp ../update-countries-map-data.mob.py update-countries-map-data.py
fi

if [[ ! -e config.py ]];
  then
    echo "user = '$1'" > config.py
    echo "photoset_id = ''" >> config.py
    echo "photo_privacy = 1" >> config.py
    echo "geo_privacy = 1" >> config.py
    echo "dont_map_tag = 'DontMap'" >> config.py
fi

if [[ ! -e coords.py ]];
  then
    echo "coords_dict = {" > coords.py
    echo "}" >> coords.py
fi
