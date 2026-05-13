#!/bin/bash

REPO_DIR="/home/pi/github/the-map-group.github.io"
GEN_MAP_DIR="/home/pi/flickr_map"

mkdir $REPO_DIR/people/$1/photos
cd $REPO_DIR/people/$1/photos
ln ../../photos.html index.html
