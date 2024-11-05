#!/bin/bash

REPO_DIR="/home/pi/github/the-map-group.github.io"
GEN_MAP_DIR="/home/pi/flickr_map"

if [ -z $1 ];
  then
    echo "Usage: ./reset-member-map.sh <member>"
    exit 1
fi

git pull origin main

cd $REPO_DIR/people/$1
rm last_total.py
rm countries.py
rm locations.py
rm user.py

./generate-map-data.py

git add countries.py
git add locations.py
git add user.py
git commit -m "Reset map for member '$1'"
git push origin main

rm countries.py
rm locations.py
rm user.py
