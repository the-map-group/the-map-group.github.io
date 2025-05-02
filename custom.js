function custom() {

  document.title = "The Map Group | Photos Map";

  addFavicon();
  addFooter();
  addBmcLogo();
  createOverlay();
  createNavButton();
  fitBoundingBox(current_bbox);

  window.onkeyup = function (event) {
    if (event.keyCode == 27) {
      closeOverlay();
    }
  }

  var group_avatar = document.createElement("IMG");
  group_avatar.setAttribute("src", "icons/map.png");
  group_avatar.setAttribute("width", "80px");
  group_avatar.setAttribute("height", "80px");
  document.getElementById("group-avatar").appendChild(group_avatar);

  var group_name = "The Map Group";
  var group_url = "https://www.flickr.com/groups/the-map-group/";

  var group_link = document.createElement("A");
  group_link.setAttribute("id", "group_link");
  group_link.setAttribute("class", "group");
  group_link.setAttribute("href", group_url);
  group_link.setAttribute("target", "_self");
  document.getElementById("group-name").appendChild(group_link);
  document.getElementById("group_link").innerText = group_name;

  if (members_list.length > 1) {
    document.getElementById("n-members").innerText = members_list.length.toString().concat(" members");
  } else {
    document.getElementById("n-members").innerText = members_list.length.toString().concat(" member");
  }

  var n_photos = 0;

  for (var i = 0; i < locations.length; i++) {
    n_photos = n_photos + locations[i][4];
  }

  document.getElementById("n-markers").addEventListener('click', function() { fitInitialBoundingBox(initial_bbox) });
  document.getElementById("n-markers").innerText = locations.length.toString();
  document.getElementById("n-photos").innerText = n_photos;

  loadMembers();

}


// Functions

function loadMembers() {

  switch (members_list_state) {
    case 1:
      // original sorting (joining date)
      for (i = 0; i < members_list_orig.length; i++) {
        members_list[i] = members_list_orig[i];
      }
      document.getElementById("menu-members").setAttribute("title", "Click to sort alphabetically");
      break;
    case 2:
      // sort by name
      members_list.sort(function(a,b) {
        var in_order = (b[2].replace(/[^a-zA-Z0-9]/g, '').toLowerCase() < a[2].replace(/[^a-zA-Z0-9]/g, '').toLowerCase());
        if (in_order) {
          return 1;
        } else {
          return -1;
        }
      });
      document.getElementById("menu-members").setAttribute("title", "Click to sort by number of markers");
      break;
    case 3:
      // sort by n_markers
      members_list.sort(function(a,b) {
        var delta = (b[4]-a[4]);
        if (delta == 0) {
          return (b[5]-a[5]);
        }
        return delta;
      });
      document.getElementById("menu-members").setAttribute("title", "Click to sort by number of photos");
      break;
    case 4:
      // sort by n_photos
      members_list.sort(function(a,b) {
        var delta = (b[5]-a[5]);
        if (delta == 0) {
          return (b[4]-a[4]);
        }
        return delta;
      });
      document.getElementById("menu-members").setAttribute("title", "Click to sort by number of countries");
      break;
    case 5:
      // sort by n_countries
      members_list.sort(function(a,b) {
        var delta = (b[6]-a[6]);
        if (delta == 0) {
          return (b[4]-a[4]);
        }
        return delta;
      });
      document.getElementById("menu-members").setAttribute("title", "Click to sort by joining date");
      break;
  }

  if (members_list.length > 1) {
    document.getElementById("n-members").innerText = members_list.length.toString().concat(" members");
  } else {
    document.getElementById("n-members").innerText = members_list.length.toString().concat(" member");
  }

  for (var i = 0; i < members_list.length; i++) {

    var member_name = members_list[i][2];
    var member_n_countries = members_list[i][6];

    var i_members_avatar = document.createElement("IMG");
    var icon_src = members_list[i][3];
    i_members_avatar.setAttribute("width", "16px");
    i_members_avatar.setAttribute("height", "16px");
    i_members_avatar.setAttribute("style", "border-radius: 50%");
    i_members_avatar.setAttribute("class", "tiny-icon");
    i_members_avatar.setAttribute("src", icon_src);
    document.getElementById("members-avatar").appendChild(i_members_avatar);

    var i_members = document.createElement("P");
    i_members.setAttribute("class", "member");
    i_members.setAttribute("id", members_list[i][0]);

    i_members.setAttribute("title", member_name.concat(", ").concat(member_n_countries).concat(" ⚑"));

    if (member_name.length > 12) {
      member_name = member_name.substring(0, 10).concat("...");
    }

    i_members.innerText = member_name;
    document.getElementById("members").appendChild(i_members);

    var i_places = document.createElement("P");
    i_places.setAttribute("class", "item");
    i_places.innerText = members_list[i][4];
    document.getElementById("places").appendChild(i_places);

    var i_places_icon = document.createElement("IMG");
    var icon_src = "icons/place.svg";
    i_places_icon.setAttribute("class", "tiny-icon");
    i_places_icon.setAttribute("src", icon_src);
    document.getElementById("place-icon").appendChild(i_places_icon);

    var i_photos = document.createElement("P");
    i_photos.setAttribute("class", "item");
    i_photos.innerText = members_list[i][5];
    document.getElementById("photos").appendChild(i_photos);

    var i_photos_icon = document.createElement("IMG");
    var icon_src = "icons/photo.svg";
    i_photos_icon.setAttribute("class", "tiny-icon");
    i_photos_icon.setAttribute("src", icon_src);
    document.getElementById("photo-icon").appendChild(i_photos_icon);
  }

  members_list.forEach(addListenerToPeople);

  document.getElementById("menu-members").setAttribute("class", "menu-active");
  document.getElementById("menu-countries").setAttribute("class", "menu-inactive");

  document.getElementById("menu-members").addEventListener('click', handleClickMembers);
  document.getElementById("menu-countries").addEventListener('click', handleClickCountries);

}

function loadCountries() {

  countries = [];

  for (var code in members_dict) {
    var n_members = members_dict[code].length;
    var n_markers = 0;
    for (var k = 0; k < members_dict[code].length; k++) {
      n_markers = n_markers + members_dict[code][k][4];
    }
    countries.push([code, countries_bbox[code], members_dict[code], n_members, n_markers]);
  };

  if (countries.length > 1) {
    document.getElementById("n-members").innerText = countries.length.toString().concat(" countries");
  } else {
    document.getElementById("n-members").innerText = countries.length.toString().concat(" country");
  }

  switch (countries_list_state) {
    case 1:
      // sort by n_members
      countries.sort(function(a,b) {
        var delta = (b[3]-a[3]);
        if (delta == 0) {
          return (b[4]-a[4]);
        }
        return delta;
      });
      document.getElementById("menu-countries").setAttribute("title", "Click to sort alphabetically");
      break;
    case 2:
      // sort alphabetically
      countries.sort(function(a,b) {
        var in_order = (b[1]<a[1]);
        if (in_order) {
          return 1;
        } else {
          return -1;
        }
      });
      document.getElementById("menu-countries").setAttribute("title", "Click to sort by number of markers");
      break;
    case 3:
      // sort by n_markers
      countries.sort(function(a,b) {
        var delta = (b[4]-a[4]);
        if (delta == 0) {
          return (b[3]-a[3]);
        }
        return delta;
      });
      document.getElementById("menu-countries").setAttribute("title", "Click to sort by number of members");
      break;
  }

  for (var i = 0; i < countries.length; i++) {

    var country_code = countries[i][0];
    console.log(country_code)
    var country_name = countries_bbox[country_code][0];
    console.log(country_name)

    var i_countries_avatar = document.createElement("IMG");
    var icon_src = getIconSrc(country_name);
    i_countries_avatar.setAttribute("width", "16px");
    i_countries_avatar.setAttribute("height", "16px");
    i_countries_avatar.setAttribute("style", "border-radius: 50%");
    i_countries_avatar.setAttribute("class", "tiny-icon");
    i_countries_avatar.setAttribute("src", icon_src);
    document.getElementById("members-avatar").appendChild(i_countries_avatar);

    var i_countries = document.createElement("P");
    i_countries.setAttribute("class", "member");
    i_countries.setAttribute("id", country_code);

    if (country_name.length > 12) {
      i_countries.setAttribute("title", country_name);
      country_name = country_name.substring(0, 10).concat("...");
    }

    i_countries.innerText = country_name;
    document.getElementById("members").appendChild(i_countries);

    var i_places = document.createElement("P");
    i_places.setAttribute("class", "item");
    i_places.innerText = countries[i][3];
    document.getElementById("places").appendChild(i_places);

    var i_places_icon = document.createElement("IMG");
    var icon_src = "icons/members.svg";
    i_places_icon.setAttribute("class", "tiny-icon");
    i_places_icon.setAttribute("src", icon_src);
    document.getElementById("place-icon").appendChild(i_places_icon);

    var i_photos = document.createElement("P");
    i_photos.setAttribute("class", "item");
    i_photos.innerText = countries[i][4];
    document.getElementById("photos").appendChild(i_photos);

    var i_photos_icon = document.createElement("IMG");
    var icon_src = "icons/place.svg";
    i_photos_icon.setAttribute("class", "tiny-icon");
    i_photos_icon.setAttribute("src", icon_src);
    document.getElementById("photo-icon").appendChild(i_photos_icon);

  }

  countries.forEach(addListenerToCountries);

  document.getElementById("menu-members").setAttribute("class", "menu-inactive");
  document.getElementById("menu-countries").setAttribute("class", "menu-active");

}

function handleClickMembers() {
  switch (members_list_state) {
    case 0:
      members_list_state = 1;
      countries_list_state = 0;
      document.getElementById("menu-countries").removeAttribute("title");
      try {
         emptyList(countries.length);
      } catch {}
      break;
    case 1:
      // sort alphabetically
      members_list_state = 2;
      emptyList(members_list.length);
      break;
    case 2:
      // sort by n_markers
      members_list_state = 3;
      emptyList(members_list.length);
      break;
    case 3:
      // sort by n_photos
      members_list_state = 4;
      emptyList(members_list.length);
      break;
    case 4:
      // sort by n_photos
      members_list_state = 5;
      emptyList(members_list.length);
      break;
    case 5:
      // original sorting (joining date)
      members_list_state = 1;
      emptyList(members_list.length);
      break;
  }
  loadMembers();
}

function handleClickCountries() {
  switch (countries_list_state) {
    case 0:
      countries_list_state = 1;
      members_list_state = 0;
      emptyList(members_list.length);
      document.getElementById("menu-members").removeAttribute("title");
      break;
    case 1:
      // sort alphabetically
      countries_list_state = 2;
      emptyList(countries.length);
      break;
    case 2:
      // sort by n_markers
      countries_list_state = 3;
      emptyList(countries.length);
      break;
    case 3:
      // sort by n_members
      countries_list_state = 1;
      emptyList(countries.length);
      break;
  }
  loadCountries();
}

function emptyList(list_size) {
  for (var i = list_size-1; i >= 0; i--) {
    var avatares_list = document.getElementById("members-avatar");
    avatares_list.removeChild(avatares_list.childNodes[i]);
    var names_list = document.getElementById("members");
    names_list.removeChild(names_list.childNodes[i]);
    var places_list = document.getElementById("places");
    places_list.removeChild(places_list.childNodes[i]);
    var place_icon_list = document.getElementById("place-icon");
    place_icon_list.removeChild(place_icon_list.childNodes[i]);
    var photos_list = document.getElementById("photos");
    photos_list.removeChild(photos_list.childNodes[i]);
    var photo_icon_list = document.getElementById("photo-icon");
    photo_icon_list.removeChild(photo_icon_list.childNodes[i]);
  }
}

function addFavicon() {
  var favicon = document.createElement("LINK");
  favicon.setAttribute("rel", "shortcut icon");
  favicon.setAttribute("type", "image/x-icon");
  favicon.setAttribute("href", "favicon.ico");
  document.head.append(favicon);
}

function createNavButton() {
  var icon = document.createElement("IMG");
  icon.setAttribute("src", "icons/people.svg");
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

  // Group Container
  var div_group_avatar = document.createElement("DIV");
  div_group_avatar.setAttribute("id", "group-avatar");
  div_group_avatar.setAttribute("class", "group-avatar");
  var div_group_name = document.createElement("DIV");
  div_group_name.setAttribute("id", "group-name");
  div_group_name.setAttribute("class", "group-name");
  var div_n_members = document.createElement("DIV");
  div_n_members.setAttribute("id", "n-members");
  div_n_members.setAttribute("class", "n-members");
  var div_u_place_icon = document.createElement("IMG");
  div_u_place_icon.setAttribute("class", "tiny-icon");
  div_u_place_icon.setAttribute("src", "icons/place.svg");
  var div_n_markers = document.createElement("DIV");
  div_n_markers.setAttribute("id", "n-markers");
  div_n_markers.setAttribute("class", "n-markers");
  var div_u_photo_icon = document.createElement("IMG");
  div_u_photo_icon.setAttribute("class", "tiny-icon");
  div_u_photo_icon.setAttribute("src", "icons/photo.svg");
  var div_n_photos = document.createElement("DIV");
  div_n_photos.setAttribute("id", "n-photos");
  div_n_photos.setAttribute("class", "n-photos");
  var div_group_container = document.createElement("DIV");
  div_group_container.setAttribute("id", "group-container");
  div_group_container.setAttribute("class", "group-container");
  div_group_container.appendChild(div_group_avatar);
  div_group_container.appendChild(div_group_name);
  div_group_container.appendChild(div_n_members);
  div_group_container.appendChild(div_u_place_icon);
  div_group_container.appendChild(div_n_markers);
  div_group_container.appendChild(div_u_photo_icon);
  div_group_container.appendChild(div_n_photos);

  // Menu Container
  var div_menu_members = document.createElement("DIV");
  div_menu_members.setAttribute("id", "menu-members");
  div_menu_members.setAttribute("class", "menu-active");
  div_menu_members.innerText = "MEMBERS";
  var div_menu_countries = document.createElement("DIV");
  div_menu_countries.setAttribute("id", "menu-countries");
  div_menu_countries.setAttribute("class", "menu-inactive");
  div_menu_countries.innerText = "COUNTRIES";
  var div_menu_container = document.createElement("DIV");
  div_menu_container.setAttribute("id", "menu-container");
  div_menu_container.setAttribute("class", "menu-container");
  div_menu_container.appendChild(div_menu_members);
  div_menu_container.appendChild(div_menu_countries);

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
  div_main_container.appendChild(div_group_container);
  div_main_container.appendChild(div_menu_container);
  div_main_container.appendChild(div_members_container);

  // Overlay
  var div_overlay_content = document.createElement("DIV");
  div_overlay_content.setAttribute("class", "overlay-content");
  div_overlay_content.appendChild(div_main_container);
  var div_overlay = document.createElement("DIV");
  div_overlay.setAttribute("id", "overlay");
  div_overlay.setAttribute("class", "overlay");
  div_overlay.setAttribute("onscroll", "changeGroupBackgroundColor()");
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
  fitBoundingBox(current_bbox);
}

function closeOverlay() {
  document.getElementById("overlay").style.width = "0%";
  document.getElementById("menu").style.display = "block";
  document.getElementById("nav-button").style.display = "block";
  document.getElementById("nav-button").style.margin = "60px 0 0 0";
  setSelectorPosition();
  fitBoundingBox(current_bbox);
}

function getIconSrc(name) {
  return "icons/flags/".concat(name.replace(/\s/g, "-").toLowerCase()).concat(".svg");
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

function addListenerToPeople(member) {
  if (member[4] > 0) {
    var member_url = "people/".concat(member[1]);
    document.getElementById(member[0]).addEventListener('click', function() { window.location.href = member_url });
  }
}

function addListenerToCountries(country) {
  var country_url = "countries/".concat(country[0].toLowerCase());
  document.getElementById(country[0]).addEventListener('click', function() { window.location.href = country_url });
}

function fitBoundingBox(bbox) {

  current_bbox = bbox;

  var overlay_status = document.getElementById("overlay").style.width;

  if (overlay_status == '400px') {
    padding_left = 450;
  } else {
    padding_left = 50;
  }

  map.fitBounds([
    [bbox[0], bbox[1]],
    [bbox[2], bbox[3]]],
    {padding: {top:50, bottom:50, left:padding_left, right:50}}
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

function changeGroupBackgroundColor() {
  if (document.getElementById("overlay").scrollTop > 25) {
    document.getElementById("group-container").className = "group-container-black";
    document.getElementById("nav-button").className = "nav-button-black";
  } else {
    document.getElementById("group-container").className = "group-container";
    document.getElementById("nav-button").className = "nav-button";
  }
}

function addFooter() {
  var footer = document.createElement("DIV");
  footer.setAttribute("class", "footer");
  footer.innerHTML = "Generated using the <a href=\"https://www.flickr.com/\" target=\"_blank\">Flick™</a> API<br>Map icon made by <a href=\"https://www.flaticon.com/authors/freepik\" title=\"Freepik\" target=\"_blank\">Freepik</a>";
  document.body.append(footer);
}

function addBmcLogo() {
  var bmc_link = document.createElement("A");
  bmc_link.setAttribute("href", "https://buymeacoffee.com/haraldo");
  bmc_link.setAttribute("target", "_blank")
  var bmc_logo = document.createElement("IMG");
  bmc_logo.setAttribute("class", "bmc_logo");
  bmc_logo.setAttribute("src", "res/bmc-button.svg");
  bmc_link.appendChild(bmc_logo);
  document.body.append(bmc_link);
}
