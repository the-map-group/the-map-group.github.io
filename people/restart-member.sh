#!/bin/bash

REPO_DIR="/home/pi/github/the-map-group.github.io"
GEN_MAP_DIR="/home/pi/flickr_map"

if [ -z $1 ];
  then
    echo "Usage: ./restart-member.sh <member>"
    exit 1
fi

cd $REPO_DIR/people/$1

if [[ ! -e api_credentials.py ]];
  then
    ln -s ../../api_credentials.py .
fi

if [[ ! -e countries_info.py ]];
  then
    ln -s ../../countries_info.py .
fi

if [[ ! -e countries_config.py ]];
  then
    ln -s ../../config.py countries_config.py
fi

if [[ ! -e matrix.py ]];
  then
    ln -s ../../matrix.py .
fi

if [[ ! -e not_found.py ]];
  then
    ln -s ../../not_found.py .
fi

if [[ ! -e countries_members.py ]];
  then
    ln -s ../../countries/members.py countries_members.py
fi

if [[ ! -e generate-map-data.py ]];
  then
    ln $GEN_MAP_DIR/generate-map-data.py .
fi

if [[ ! -e index.html ]];
  then
    ln ../index.html .
fi

if [[ ! -e update-countries-map-data.py ]];
  then
    ln ../update-countries-map-data.py .
fi

if [[ -e last_total.py ]];
  then
    rm last_total.py
fi

if [[ -e user.py ]];
  then
    rm user.py
fi

if [[ -e countries.py ]];
  then
    rm countries.py
fi

if [[ -e locations.py ]];
  then
    rm locations.py
fi

if [[ -e __pycache__ ]];
  then
    rm -r __pycache__
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
