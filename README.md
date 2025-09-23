# The Map Group

This is the code repository for the [Flickr](https://www.flickr.com)'s group [**The Map Group**](https://www.flickr.com/groups/the-map-group/).

The group's purpose is to generate maps for the members, containing their geo-tagged photos, and also a map for the group itself, containing the photos posted to the [group's pool](https://www.flickr.com/groups/the-map-group/pool/), by members or by owners of invited photos.

### Group's Map

The group's map contains a panel with links to each member's _Flickr_ photostream and shows the number of markers and photos that he or she added to the group.
Clicking on a marker it is possible to see the photo(s) taken on the corresponding location. Clicking on the photo thumbnail opens the photo's page on _Flickr_.

[![Group Map](https://live.staticflickr.com/65535/50277109767_97bc59c58b_b.jpg)](https://the-map-group.top/)

### Member's Map

The member's maps contain a panel with a list of all the countries where the member have taken photos and uploaded to _Flickr_. Clicking on the country makes the map zoom to it.
The markers have the same behaviour of the group's map.

[![Member Map](https://live.staticflickr.com/65535/50276281928_9817158c15_b.jpg)](https://the-map-group.top/people/hpfilho)

## Maps Generation

### Map Data

The maps data are generated using the script [FlickrMap](https://github.com/the-map-group/flickr-map), writen in _**Python**_. This script uses the [_Flickr API_](https://www.flickr.com/services/api/)
to get the photos data. It generates the following files:

- **locations.py**: Contains all the markers information, as coordinates and photos attached to them.
- **countries.py**: List of countries where the photos were taken, including number of places and photos for each place.
- **user.py**: Basic user information, such as user id, name, avatar url, photostream url, number of markers and photos on map.

The data on these files are read by a _**Javascript**_ code embedded in a html page, which loads the map. The panel and other customizations are coded in separated _**Javascript**_ and _**CSS**_ files.

### Map Renderization

The map is provided by [_Mapbox_](https://www.mapbox.com/), using its [_Mapbox GL JS API_](https://docs.mapbox.com/mapbox-gl-js/api/) to populate it with the markers data.
