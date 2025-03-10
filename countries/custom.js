function custom() {

  var country_name = countries_bbox[country_code][0];

  document.title = country_name.concat(" | Photos Map");

  addFavicon();
  addAttribution();
  createOverlay();
  createNavButton();
  fitBoundingBox(current_bbox);

  window.onkeyup = function (event) {
    if (event.keyCode == 27) {
      closeOverlay();
    }
  }

  var country_avatar = document.createElement("IMG");
  country_avatar.setAttribute("src", getIconSrc(country_name));
  country_avatar.setAttribute("width", "80px");
  country_avatar.setAttribute("height", "80px");
  document.getElementById("country-avatar").appendChild(country_avatar);

  var members = members_dict[country_code];

  var members_list = [];

  for (var i = 0; i < members.length; i++) {
    members_list.push(members[i][0]);
  }

  var country_link = document.createElement("A");

  if (country_name.length > 17) {
    country_link.setAttribute("title", country_name);
    country_name = country_name.substring(0, 14).concat("...");
  }

  country_link.setAttribute("id", "country_link");
  country_link.setAttribute("class", "country");
  document.getElementById("country-name").appendChild(country_link);
  document.getElementById("country_link").innerText = country_name;

  if (members.length > 1) {
    document.getElementById("n-members").innerText = members.length.toString().concat(" members");
  } else {
    document.getElementById("n-members").innerText = members.length.toString().concat(" member");
  }

  var n_markers = 0;
  var n_photos = 0;

  for (var i = 0; i < country_locations.length; i++) {
      n_markers++;
      n_photos = n_photos + country_locations[i][4];
  }

  document.getElementById("n-markers").addEventListener('click', function() { fitInitialBoundingBox(initial_bbox) });
  document.getElementById("n-markers").innerText = n_markers;
  document.getElementById("n-photos").innerText = n_photos;

  members.sort(function(a,b) {
    var delta = (b[4]-a[4]);
    if (delta == 0) {
      return (b[5]-a[5]);
    }
    return delta;
   });


  for (var i = 0; i < members.length; i++) {

    var member_name = members[i][2];

    var i_members_avatar = document.createElement("IMG");
    var icon_src = members[i][3];
    i_members_avatar.setAttribute("width", "16px");
    i_members_avatar.setAttribute("height", "16px");
    i_members_avatar.setAttribute("style", "border-radius: 50%");
    i_members_avatar.setAttribute("class", "tiny-icon");
    i_members_avatar.setAttribute("src", icon_src);
    document.getElementById("members-avatar").appendChild(i_members_avatar);

    var i_members = document.createElement("P");
    i_members.setAttribute("class", "member");
    i_members.setAttribute("id", members[i][0]);

    if (member_name.length > 12) {
      i_members.setAttribute("title", member_name);
      member_name = member_name.substring(0, 10).concat("...");
    }

    i_members.innerText = member_name;
    document.getElementById("members").appendChild(i_members);

    var i_places = document.createElement("P");
    i_places.setAttribute("class", "item");
    i_places.innerText = members[i][4];
    document.getElementById("places").appendChild(i_places);

    var i_places_icon = document.createElement("IMG");
    var icon_src = "../../icons/place.svg";
    i_places_icon.setAttribute("class", "tiny-icon");
    i_places_icon.setAttribute("src", icon_src);
    document.getElementById("place-icon").appendChild(i_places_icon);

    var i_photos = document.createElement("P");
    i_photos.setAttribute("class", "item");
    i_photos.innerText = members[i][5];
    document.getElementById("photos").appendChild(i_photos);

    var i_photos_icon = document.createElement("IMG");
    var icon_src = "../../icons/photo.svg";
    i_photos_icon.setAttribute("class", "tiny-icon");
    i_photos_icon.setAttribute("src", icon_src);
    document.getElementById("photo-icon").appendChild(i_photos_icon);
  }

  members.forEach(addListener);

}


// Functions

function addFavicon() {
  var favicon = document.createElement("LINK");
  favicon.setAttribute("rel", "shortcut icon");
  favicon.setAttribute("type", "image/x-icon");
  favicon.setAttribute("href", "../../favicon.ico");
  document.head.append(favicon);
}

function createNavButton() {
  var icon = document.createElement("IMG");
  icon.setAttribute("src", "../../icons/people.svg");
  icon.setAttribute("height", "24px");
  icon.setAttribute("width", "24px");
  var div_nav_button = document.createElement("DIV");
  div_nav_button.setAttribute("id", "nav-button");
  div_nav_button.setAttribute("class", "nav-button");
  div_nav_button.setAttribute("onclick", "toggleOverlay()");
  div_nav_button.appendChild(icon);
  document.body.append(div_nav_button);
}

function createOverlay() {

  // country Container
  var div_country_avatar = document.createElement("DIV");
  div_country_avatar.setAttribute("id", "country-avatar");
  div_country_avatar.setAttribute("class", "country-avatar");
  var div_country_name = document.createElement("DIV");
  div_country_name.setAttribute("id", "country-name");
  div_country_name.setAttribute("class", "country-name");
  var div_n_members = document.createElement("DIV");
  div_n_members.setAttribute("id", "n-members");
  div_n_members.setAttribute("class", "n-members");
  var div_u_place_icon = document.createElement("IMG");
  div_u_place_icon.setAttribute("class", "tiny-icon");
  div_u_place_icon.setAttribute("src", "../../icons/place.svg");
  var div_n_markers = document.createElement("DIV");
  div_n_markers.setAttribute("id", "n-markers");
  div_n_markers.setAttribute("class", "n-markers");
  var div_u_photo_icon = document.createElement("IMG");
  div_u_photo_icon.setAttribute("class", "tiny-icon");
  div_u_photo_icon.setAttribute("src", "../../icons/photo.svg");
  var div_n_photos = document.createElement("DIV");
  div_n_photos.setAttribute("id", "n-photos");
  div_n_photos.setAttribute("class", "n-photos");
  var div_country_container = document.createElement("DIV");
  div_country_container.setAttribute("id", "country-container");
  div_country_container.setAttribute("class", "country-container");
  div_country_container.appendChild(div_country_avatar);
  div_country_container.appendChild(div_country_name);
  div_country_container.appendChild(div_n_members);
  div_country_container.appendChild(div_u_place_icon);
  div_country_container.appendChild(div_n_markers);
  div_country_container.appendChild(div_u_photo_icon);
  div_country_container.appendChild(div_n_photos);

  // Members Container
  var div_members_avatar = document.createElement("DIV");
  div_members_avatar.setAttribute("id", "members-avatar");
  div_members_avatar.setAttribute("class", "members-avatar");
  var div_members = document.createElement("DIV");
  div_members.setAttribute("id", "members");
  div_members.setAttribute("class", "members");
  var div_places = document.createElement("DIV");
  div_places.setAttribute("id", "places");
  div_places.setAttribute("class", "places");
  var div_place_icon = document.createElement("DIV");
  div_place_icon.setAttribute("id", "place-icon");
  div_place_icon.setAttribute("class", "place-icon");
  var div_photos = document.createElement("DIV");
  div_photos.setAttribute("id", "photos");
  div_photos.setAttribute("class", "photos");
  var div_photo_icon = document.createElement("DIV");
  div_photo_icon.setAttribute("id", "photo-icon");
  div_photo_icon.setAttribute("class", "photo-icon");
  var div_members_container = document.createElement("DIV");
  div_members_container.setAttribute("id", "members-container");
  div_members_container.setAttribute("class", "members-container");
  div_members_container.appendChild(div_members_avatar);
  div_members_container.appendChild(div_members);
  div_members_container.appendChild(div_places);
  div_members_container.appendChild(div_place_icon);
  div_members_container.appendChild(div_photos);
  div_members_container.appendChild(div_photo_icon);

  // Main container
  var div_main_container = document.createElement("DIV");
  div_main_container.setAttribute("id", "main-container");
  div_main_container.setAttribute("class", "main-container");
  div_main_container.appendChild(div_country_container);
  div_main_container.appendChild(div_members_container);

  // Overlay
  var div_overlay_content = document.createElement("DIV");
  div_overlay_content.setAttribute("class", "overlay-content");
  div_overlay_content.appendChild(div_main_container);
  var div_overlay = document.createElement("DIV");
  div_overlay.setAttribute("id", "overlay");
  div_overlay.setAttribute("class", "overlay");
  div_overlay.setAttribute("onscroll", "changecountryBackgroundColor()");
  div_overlay.appendChild(div_overlay_content);
  div_overlay.style.width = "0%";

  document.body.append(div_overlay);

  setSelectorPosition();

}

function toggleOverlay() {
  var selector_position
  var pixels;
  if (document.getElementById("overlay").style.width == "0%") {
    openOverlay();
  } else {
    closeOverlay();
  }
  fitBoundingBox(current_bbox);
}

function openOverlay() {
  document.getElementById("overlay").style.width = "400px";
  document.getElementById("menu").style.display = "none";
  document.getElementById("nav-button").style.margin = "60px 0 0 400px";
  setSelectorPosition();
}

function closeOverlay() {
  document.getElementById("overlay").style.width = "0%";
  document.getElementById("menu").style.display = "block";
  document.getElementById("nav-button").style.display = "block";
  document.getElementById("nav-button").style.margin = "60px 0 0 0";
  setSelectorPosition();
}

function getIconSrc(name) {
  return "../../icons/flags/".concat(name.replace(/\s/g, "-").toLowerCase()).concat(".svg");
}

function setSelectorPosition() {
  var pixels;
  if (document.getElementById("overlay").style.width == "0%") {
    pixels = (window.innerWidth-150)/2;
  } else {
    pixels = (window.innerWidth+100)/2;
  }
  var selector_position = pixels.toString() + "px";
  document.getElementById("selector").style.left = selector_position;
}

function addListener(member) {
  var member_url = "../../people/".concat(member[1]).concat("/?country=").concat(country_code);
  document.getElementById(member[0]).addEventListener('click', function() { window.location.replace(member_url) });
}

function fitBoundingBox(bbox) {

  current_bbox = bbox;

  var overlay_status = document.getElementById("overlay").style.width;

  if (overlay_status == '400px') {
    padding_left = 450;
  } else {
    padding_left = 100;
  }

  map.fitBounds([
    [bbox[0], bbox[1]],
    [bbox[2], bbox[3]]],
    {padding: {top:100, bottom:100, left:padding_left, right:100}}
  );

};

function fitInitialBoundingBox(initial_bbox) {

  var overlay_status = document.getElementById("overlay").style.width;

  if (overlay_status == '400px') {
    padding_left = 450;
  } else {
    padding_left = 50;
  }

  map.fitBounds([
    [initial_bbox[0], initial_bbox[1]],
    [initial_bbox[2], initial_bbox[3]]],
    {padding: {top:50, bottom:50, left:padding_left, right:50}}
  );

  current_bbox = initial_bbox;

};

function changecountryBackgroundColor() {
  if (document.getElementById("overlay").scrollTop > 25) {
    document.getElementById("country-container").className = "country-container-black";
    document.getElementById("nav-button").className = "nav-button-black";
  } else {
    document.getElementById("country-container").className = "country-container";
    document.getElementById("nav-button").className = "nav-button";
  }
}

function addAttribution() {
  var attrib = document.createElement("DIV");
  attrib.setAttribute("class", "attribution");
  attrib.innerHTML = "Map generated using the <a href=\"https://www.flickr.com/\">Flick™</a> API.<br>Flag icon made by <a href=\"https://www.flaticon.com/authors/freepik\" title=\"Freepik\">Freepik</a> from <a href=\"https://www.flaticon.com/\" title=\"Flaticon\">www.flaticon.com</a>";
  document.body.append(attrib);
}
