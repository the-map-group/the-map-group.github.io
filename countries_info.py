#!/usr/bin/python3

from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
from geopy.geocoders import MapBox

import os
import api_credentials
import countries_config
import not_found

try:
    geolocator1 = Nominatim(user_agent=api_credentials.nominatim_agent)
    geolocator2 = GeoNames(username=api_credentials.geonames_user)
except:
    print("ERROR: FATAL: Unable to get geolocators")
    sys.exit()

def isTerritory(lat, long, code):
    try:
        for coords in countries_dict[code][1]:
            if long > coords[0] and lat > coords[1] and long < coords[2] and lat < coords[3]:
                return False
    except:
        pass
    return True

def getInfoFromCoordsDict(latlong, coords_dict):
    country_info = ['', '']
    key = "{},{}".format(latlong[0], latlong[1])
    try:
        country_info = coords_dict[key]
    except:
        pass
    return country_info

def getInfoFromNominatim(latlong):
    code = ''
    name = ''
    try:
        location = geolocator1.reverse(latlong, language='en-US', zoom=18, exactly_one=True)
        if location != None:
            code = location.raw['address']['country_code'].upper()
            name = location.raw['address']['country']
    except:
        code = '*'
    return [code, name]

def getInfoFromGeoNames(latlong):
    code = ''
    name = ''
    try:
        location = geolocator2.reverse(latlong, lang='en-US', exactly_one=True)
        if location != None:
            code = location.raw['countryCode']
            name = location.raw['countryName']
    except:
        code = '*'
    return [code, name]

def getInfoFromMapBox(latlong):
    code = ''
    name = ''
    try:
        geolocator3 = MapBox(api_key=api_credentials.mapbox_token)
    except:
        return ['**', '']
    try:
        location = geolocator3.reverse(latlong, exactly_one=True)
        if location != None:
            location_info = location.raw['context']
            len_info = len(location_info)
            if len_info > 4:
                info_index = 3
            else:
                info_index = len_info - 1
            code = location_info[info_index]['short_code'].upper()
            name = location_info[info_index]['text']
            if len(code) > 2:
                code = code[:2]
    except:
        code = '*'
        name = ''
    return [code, name]

def getCountryInfo(lat, long, coords_dict):

    use_matrix = countries_config.use_matrix
    use_mapbox = countries_config.use_mapbox
    nominatim_exclude = countries_config.nominatim_exclude
    geonames_exclude = countries_config.geonames_exclude
    gen_err_file = countries_config.gen_err_file
    gen_rep_file = countries_config.gen_rep_file
    rep_matrix = countries_config.rep_matrix
    rep_dictionary = countries_config.rep_dictionary
    rep_nominatim = countries_config.rep_nominatim
    rep_geonames = countries_config.rep_geonames
    rep_mapbox = countries_config.rep_mapbox

    is_territory = False

    run_dir = os.path.dirname(os.path.realpath(__file__))

    log_dir = "{}/log".format(run_dir)
    if not os.path.isdir(log_dir):
        os.system("mkdir {}".format(log_dir))

    htm_file = open("{}/index.html".format(log_dir), "a")
    log_file = open("{}/countries_info.log".format(log_dir), "a")

    if gen_err_file:
        err_file = open("{}/countries_info.err".format(log_dir), "a")

    if gen_rep_file:
        rep_file = open("{}/countries_info.rep".format(log_dir), "a")

    try:
        if not gen_err_file and os.path.isfile("{}/countries_info.err".format(log_dir)):
            os.system("git rm {}/countries_info.err".format(log_dir))
        if not gen_rep_file and os.path.isfile("{}/countries_info.rep".format(log_dir)):
            os.system("git rm {}/countries_info.rep".format(log_dir))
    except:
        pass

    latlong = (lat, long)
    latitude = int(lat)
    longitude = int(long)
    lat_long = [latitude, longitude]

    try:
        not_found_places_list = not_found.coords
        not_found_places_excludes = not_found.excludes
    except:
        print("ERROR: FATAL: Unable to load the not found places list. File not_found.py doesn\'t exist.")
        sys.exit()

    if lat_long in not_found_places_list and lat_long not in not_found_places_excludes:
        log_file.write("{} skipped: [{}, {}] is at not found list\n".format(latlong, latitude, longitude))
        log_file.close()
        htm_file.close()
        if gen_rep_file:
            rep_file.close()
        if gen_err_file:
            err_file.close()
        code = ''
        name = ''
        return [code, name, coords_dict]
    elif lat_long in not_found_places_excludes:
            log_file.write("{} not skipped: [{}, {}] is at not found excludes\n".format(latlong, latitude, longitude))

    if use_matrix:
        try:
            lat_codes = latitude_dict[latitude]
            long_codes = longitude_dict[longitude]
            codes = lat_codes.intersection(long_codes)
        except:
            if gen_err_file:
                err_file.write("Matrix: ERROR: Key error at [{}, {}]\n".format(latitude, longitude))
            codes = []

    if use_matrix and len(codes) == 1:
        code = codes.pop()
        name = countries_dict[code][0]
        if gen_rep_file and rep_matrix:
            rep_file.write("Matrix: {} = [{}, {}] => '{}: {}'\n".format(latlong, latitude, longitude, code, name))
    else:

        # get info from coordinates dictionary
        info = getInfoFromCoordsDict(latlong, coords_dict)
        code = info[0]
        name = info[1]

        if code != '':
            if gen_rep_file:
                if rep_dictionary:
                    rep_file.write("Dictionary: {} = '{}: {}'\n".format(latlong, code, name))
                rep_file.close()
            if gen_err_file:
                err_file.close()
            log_file.close()
            htm_file.close()

            return [code, name, coords_dict]

        # get info from Nominatim if not found in dictionary
        if code == '':

            info = getInfoFromNominatim(latlong)
            code = info[0]
            name = info[1]

            if code == '*' or code in nominatim_exclude:
                code = ''
                name = ''

            if isTerritory(lat, long, code):
                code = ''
                name = ''

            if code != '':
                if gen_rep_file and rep_nominatim:
                    rep_file.write("-> Nominatim: {} = '{}: {}'\n".format(latlong, code, name))
            elif gen_err_file:
                err_file.write("-> Nominatim: {} = NOT FOUND\n".format(latlong))

        # get info from GeoNames if not found by Nominatim
        if code == '':

            info = getInfoFromGeoNames(latlong)
            code = info[0]
            name = info[1]

            if (code == '*' and use_mapbox) or code in geonames_exclude:
                code = ''
                name = ''

            if code != '' and code != '*':
                if gen_rep_file and rep_geonames:
                    rep_file.write("--> GeoNames: {} = '{}: {}'\n".format(latlong, code, name))
            elif gen_err_file:
                err_file.write("--> GeoNames: {} = NOT FOUND\n".format(latlong))

        # assign correct code and name to some countries using the dictionaries
        try:
            if name != countries_dict[code][0]:
                if gen_rep_file:
                    rep_file.write("\'{}: {}\' = \'{}\' ".format(code, name, countries_dict[code][0]))
                try:
                    code = codes_dict[name]
                    name = countries_dict[code][0]
                    if gen_rep_file:
                        rep_file.write("=> \'{}: {}'\n".format(code, name))
                except:
                    if gen_rep_file:
                        rep_file.write("\n")
        except:
            if code != '' and code != '*':
                rep_file.write("\'{}: {}\' = NOT FOUND AT DICTIONARY\n".format(code, name))

        # check if location is in a territory of another country
        try:
            is_territory = isTerritory(lat, long, code)
            if is_territory and name == countries_dict[code][0]:
                htm_file.write("(<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}&marker=1\" target=\"_blank\">{0}, {1}</a>) is in a territory of \'{2}\': \n".format(lat, long, name))
                log_file.write("{} is in a territory of \'{}\': ".format(latlong, name))
        except:
            pass

        # get the correct info from MapBox if location is in a territory of another country
        if use_mapbox and (code == '' or is_territory):

            info = getInfoFromMapBox(latlong)
            code = info[0]
            name = info[1]

            if gen_err_file and (code == '' or code == '*'):
                err_file.write("---> MapBox: {} = NOT FOUND\n".format(latlong))

            if gen_err_file and code == '**':
                if gen_err_file:
                    err_file.write("---> MapBox: ERROR: Unable to get geolocator\n")

            if code != '' and code != '*' and code != '**':
                if is_territory:
                    htm_file.write("\'{}: {}\' found by MapBox geocoder<br>\n".format(code, name))
                if gen_rep_file and rep_mapbox:
                    rep_file.write("---> MapBox: {} => \'{}: {}\'\n".format(latlong, code, name))

        if not use_mapbox and (code == '' or is_territory):

            if is_territory:
                htm_file.write("unable to find the name of the location<br>\n".format(code, name))
                log_file.write("unable to find the name of the location\n".format(code, name))

        # assign correct code and name to some countries using the dictionaries
        try:
            if name != countries_dict[code][0]:
                if gen_rep_file:
                    rep_file.write("\'{}: {}\' = \'{}\' ".format(code, name, countries_dict[code][0]))
                try:
                    code = codes_dict[name]
                    name = countries_dict[code][0]
                    if gen_rep_file:
                        rep_file.write("=> \'{}: {}'\n".format(code, name))
                except:
                    if gen_rep_file:
                        rep_file.write("\n")
        except:
            if code != '' and code != '*':
                rep_file.write("\'{}: {}\' = NOT FOUND AT DICTIONARY\n".format(code, name))

        # add coordinate to dicitionary
        if code != '' and code != '*' and code != '**':
            latlong_key = "{},{}".format(latlong[0], latlong[1])
            coords_dict[latlong_key] = [code, name]

        # location not found by any of the geocoders, decide if coordinates are added to not found list
        if code == '':
            htm_file.write("(<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}&marker=1\" target=\"_blank\">{0}, {1}</a>) not found by any of the geocoders: ".format(lat, long))
            log_file.write("{} not found by any of the geocoders: ".format(latlong))
            if lat_long not in not_found_places_excludes:
                inc_lat = 1
                inc_long = 1
                if latitude < 0:
                    inc_lat = -1
                if longitude < 0:
                    inc_long = -1
                try:
                    coord_01 = (latitude, longitude + inc_long)
                    coord_10 = (latitude + inc_lat, longitude)
                    coord_11 = (latitude + inc_lat, longitude + inc_long)
                    if use_mapbox:
                        code_01 = getInfoFromMapBox(coord_01)[0]
                        code_10 = getInfoFromMapBox(coord_10)[0]
                        code_11 = getInfoFromMapBox(coord_11)[0]
                    else:
                        code_01 = getInfoFromGeoNames(coord_01)[0]
                        code_10 = getInfoFromGeoNames(coord_10)[0]
                        code_11 = getInfoFromGeoNames(coord_11)[0]

                    if code_01 == '' and code_10 == '' and code_11 == '':
                        not_found_places_list.append(lat_long)
                        htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> added to not found list<br>\n".format(latitude, longitude))
                        log_file.write("[{}, {}] added to not found list\n".format(latitude, longitude))
                    elif code_01 != '*' and code_10 != '*' and code_11 != '*' and code_01 != '**' and code_10 != '**' and code_11 != '**':
                        not_found_places_excludes.append(lat_long)
                        htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> is not in an isolated place, added to not found excludes<br>\n".format(latitude, longitude))
                        log_file.write("[{}, {}] is not in an isolated place, added to not found excludes\n".format(latitude, longitude))
                    else:
                        htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> not added to not found list or excludes, an exception ocurred<br>\n".format(latitude, longitude))
                        log_file.write("[{}, {}] not added to not found list or excludes, an exception ocurred\n".format(latitude, longitude))
                    not_found_file = open("{}/not_found.py".format(run_dir), "w")
                    not_found_file.write("coords = [\n")
                    for coord in not_found_places_list:
                        not_found_file.write("  [{}, {}],\n".format(coord[0], coord[1]))
                    not_found_file.write("]\n\n")
                    not_found_file.write("excludes = [\n")
                    for exclude in not_found_places_excludes:
                        not_found_file.write("  [{}, {}],\n".format(exclude[0], exclude[1]))
                    not_found_file.write("]\n")
                    not_found_file.close()
                except:
                    htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> not added to not found list or excludes, an exception ocurred<br>\n".format(latitude, longitude))
                    log_file.write("[{}, {}] not added to not found list or excludes, an exception ocurred\n".format(latitude, longitude))
            else:
                htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> is at not found excludes<br>\n".format(latitude, longitude))
                log_file.write("[{}, {}] is at not found excludes\n".format(latitude, longitude))
        elif code == '*':
            htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> not added to not found list or excludes, unable to get location<br>\n".format(latitude, longitude))
            log_file.write("[{}, {}] not added to not found list or excludes, unable to get location\n".format(latitude, longitude))
        elif code == '**':
            htm_file.write("<a href=\"https://the-map-group.top/log/map/?lat={0}&long={1}\" target=\"_blank\">[{0}, {1}]</a> not added to not found list or excludes, unable to get geolocator<br>\n".format(latitude, longitude))
            log_file.write("[{}, {}] not added to not found list or excludes, unable to get geolocator\n".format(latitude, longitude))

        htm_file.close()
        log_file.close()
        if gen_rep_file:
            rep_file.close()
        if gen_err_file:
            err_file.close()

        if code == '*' or code == '**':
            code = ''
            name = ''

    return [code, name, coords_dict]


# dictionaries

countries_dict = {
    'AD': ['Andorra', [[1.405404, 42.427745, 1.795418, 42.656415]]],
    'AE': ['United Arab Emirates', [[51.5795186705, 22.4969475367, 56.3968473651, 26.055464179]]],
    'AF': ['Afghanistan', [[60.5284298033, 29.318572496, 75.1580277851, 38.4862816432]]],
    'AG': ['Antigua and Barbuda', [[-62.359054, 16.929362, -61.640823, 17.744734]]],
    'AI': ['Anguilla', [[-63.464673, 18.132158, -62.903737, 18.602913]]],
    'AL': ['Albania', [[19.3044861183, 39.624997667, 21.0200403175, 42.6882473822]]],
    'AM': ['Armenia', [[43.5827458026, 38.7412014837, 46.5057198423, 41.2481285671]]],
    'AO': ['Angola', [[11.6400960629, -17.9306364885, 24.0799052263, -4.43802336998]]],
    'AQ': ['Antarctica', [[-179.999, -90, 179.999, -58]]],
    'AR': ['Argentina', [[-73.4154357571, -55.25, -53.628348965, -21.8323104794]]],
    'AT': ['Austria', [[9.47996951665, 46.4318173285, 16.9796667823, 49.0390742051]]],
    'AU': ['Australia', [[111.338953078, -44.6345972634, 164.569469029, -9.6681857235]]],
    'AW': ['Aruba', [[-70.29452679952362, 12.407243342751821, -69.82504218458341, 12.639490542218121]]],
    'AZ': ['Azerbaijan', [[44.7939896991, 38.2703775091, 50.3928210793, 41.8606751572]]],
    'BA': ['Bosnia and Herzegovina', [[15.7500260759, 42.65, 19.59976, 45.2337767604]]],
    'BB': ['Barbados', [[-59.665815, 13.045699, -59.417162, 13.344526]]],
    'BD': ['Bangladesh', [[88.0844222351, 20.670883287, 92.6727209818, 26.4465255803]]],
    'BE': ['Belgium', [[2.51357303225, 49.5294835476, 6.35665815596, 51.4750237087]]],
    'BF': ['Burkina Faso', [[-5.47056494793, 9.61083486576, 2.17710778159, 15.1161577418]]],
    'BG': ['Bulgaria', [[22.3805257504, 41.2344859889, 29.5580814959, 44.2349230007]]],
    'BH': ['Bahrain', [[50.2470347746, 25.7659864082, 50.7709381768, 26.3683130773]]],
    'BI': ['Burundi', [[29.0249263852, -4.49998341229, 30.752262811, -2.34848683025]]],
    'BJ': ['Benin', [[0.772335646171, 6.14215770103, 3.79711225751, 12.2356358912]]],
    'BM': ['Bermuda', [[-64.893439, 32.244335, -64.642937, 32.393605]]],
    'BN': ['Brunei', [[114.204016555, 4.007636827, 115.450710484, 5.44772980389]]],
    'BO': ['Bolivia', [[-69.5904237535, -22.8729187965, -57.4983711412, -9.76198780685]]],
    'BQ': ['Bonaire', [[-69.432215, 12.021435, -63.161908, 18.355929]]],
    'BR': ['Brazil', [[-73.9872354804, -33.7683777809, -28.7299934555, 5.24448639569]]],
    'BS': ['Bahamas', [[-79.98, 20.51, -71.0, 27.24]]],
    'BT': ['Bhutan', [[88.8142484883, 26.7194029811, 92.1037117859, 28.2964385035]]],
    'BW': ['Botswana', [[19.8954577979, -26.8285429827, 29.4321883481, -17.6618156877]]],
    'BY': ['Belarus', [[23.1994938494, 51.3195034857, 32.6936430193, 56.1691299506]]],
    'BZ': ['Belize', [[-89.2291216703, 15.8869375676, -87.1068129138, 18.4999822047]]],
    'CA': ['Canada', [[-140.99778, 41.6751050889, -52.6480987209, 83.23324]]],
    'CD': ['Democratic Republic of the Congo', [[12.1823368669, -13.2572266578, 31.1741492042, 5.25608775474]]],
    'CF': ['Central African Republic', [[14.4594071794, 2.2676396753, 27.3742261085, 11.1423951278]]],
    'CG': ['Congo', [[11.0937728207, -5.03798674888, 18.4530652198, 3.72819651938]]],
    'CH': ['Switzerland', [[6.02260949059, 45.7769477403, 10.5427014502, 47.8308275417]]],
    'CI': ['Ivory Coast', [[-8.60288021487, 4.33828847902, -2.56218950033, 10.5240607772]]],
    'CK': ['Cook Islands', [[-159.951493, -22.024598, -157.156169, -18.819687]]],
    'CL': ['Chile', [[-75.6443953112, -56.61183, -65.95992, -17.5800118954], [-109.50362444697001, -27.230656820598767, -109.18057943196189, -27.03105539474612]]],
    'CM': ['Cameroon', [[8.48881554529, 1.72767263428, 16.0128524106, 12.8593962671]]],
    'CN': ['China', [[73.6753792663, 18.197700914, 135.026311477, 53.4588044297]]],
    'CO': ['Colombia', [[-78.9909352282, -4.29818694419, -66.8763258531, 12.6373031682]]],
    'CR': ['Costa Rica', [[-85.94172543, 8.22502798099, -82.5461962552, 11.2171192489]]],
    'CU': ['Cuba', [[-85.9749110583, 19.8554808619, -74.1480248685, 23.8886107447]]],
    'CV': ['Cape Verde', [[-25.455971, 14.706625, -22.497389, 17.224064]]],
    'CW': ['Curaçao', [[-69.21882845380156, 12.029359492620058, -68.65303257484364, 12.418583596006405]]],
    'CY': ['Cyprus', [[32.2566671079, 34.5718694118, 34.1048808123, 35.3931247015]]],
    'TY': ['Northern Cyprus', [[32.58167868811915, 34.964828049823055, 34.74720840589335, 35.7570382711454]]],
    'CZ': ['Czech Republic', [[12.2401111182, 48.5553052842, 18.8531441586, 51.1172677679]]],
    'DE': ['Germany', [[5.98865807458, 47.3024876979, 15.0169958839, 55.983104153]]],
    'DJ': ['Djibouti', [[41.66176, 10.9268785669, 43.3178524107, 12.6996385767]]],
    'DK': ['Denmark', [[6.08997684086, 54.6000145534, 15.6900061378, 57.930016588], [14.613165202397736, 54.96661755000927, 15.272102304381914, 55.322660495963795]]],
    'DM': ['Dominica', [[-61.470812, 15.208117, -61.235424, 15.647632]]],
    'DO': ['Dominican Republic', [[-71.9451120673, 17.598564358, -68.3179432848, 20.8849105901]]],
    'DZ': ['Algeria', [[-8.68439978681, 19.0573642034, 11.9995056495, 37.1183806422]]],
    'EC': ['Ecuador', [[-80.9677654691, -4.95912851321, -75.2337227037, 1.3809237736], [-91.78482012101239, -1.5824948711196969, -88.75636188841905, 0.9042588609438755]]],
    'EE': ['Estonia', [[21.3397953631, 57.4745283067, 28.2316992531, 59.6110903998]]],
    'EG': ['Egypt', [[24.70007, 22.0, 36.86623, 33.58568]]],
    'EH': ['Western Sahara', [[-17.443494, 20.589817, -8.538591, 27.733945]]],
    'ER': ['Eritrea', [[36.3231889178, 12.4554157577, 43.3812260272, 17.9983074]]],
    'ES': ['Spain', [[-10.39288367353, 35.926850084, 5.43948408368, 43.7483377142], [-18.569668805804973, 27.43668482526088, -12.972592777381738, 29.47483064876065], [-5.392763536146292, 35.86627481887327, -5.26521914459584, 35.92426331993819]]],
    'ET': ['Ethiopia', [[32.95418, 3.42206, 47.78942, 14.95943]]],
    'EU': ['European Union', [[-24.689924, 35.716942, 50.678160, 71.093955]]],
    'FI': ['Finland', [[20.6455928891, 59.746373196, 31.5160921567, 70.1641930203]]],
    'FJ': ['Fiji', [[-180.0, -18.28799, 180.0, -16.0208822567]]],
    'FK': ['Falkland Islands', [[-62.0, -52.3, -57.65, -50.9]]],
    'FM': ['Micronesia', [[138, 0, 164, 10]]],
    'FO': ['Faroe Islands', [[-7.723461, 61.381658, -6.215588, 62.396159]]],
    'FR': ['France', [[-7.616257, 42.417756, 9.56001631027, 51.3485061713], [8.425295708550317, 41.30316477790055, 9.614212396017411, 43.06493582438865]]],
    'GA': ['Gabon', [[8.79799563969, -3.97882659263, 14.4254557634, 2.32675751384]]],
    'GB': ['United Kingdom', [[-9.57216793459, 48.759999905, 2.78153079591, 58.6350001085]]],
    'GD': ['Grenada', [[ -61.813504, 11.989115, -61.363392, 12.540112]]],
    'GE': ['Georgia', [[39.9550085793, 41.0644446885, 46.6379081561, 43.553104153]]],
    'GG': ['Guernsey', [[-2.790948, 49.313433, -2.149365, 50.135901]]],
    'GH': ['Ghana', [[-3.24437008301, 4.71046214438, 1.0601216976, 11.0983409693]]],
    'GI': ['Gibraltar', [[-5.457244, 36.008739, -5.337133, 36.155070]]],
    'GL': ['Greenland', [[-73.297, 60.03676, -12.20855, 83.64513]]],
    'GM': ['Gambia', [[-16.8415246241, 13.1302841252, -13.8449633448, 13.8764918075]]],
    'GN': ['Guinea', [[-15.1303112452, 7.3090373804, -7.83210038902, 12.5861829696]]],
    'GP': ['Guadeloupe', [[-61.832560, 15.818848, -60.572362, 16.615294]]],
    'GQ': ['Equatorial Guinea', [[9.3056132341, 1.01011953369, 11.285078973, 2.28386607504]]],
    'GR': ['Greece', [[ 19.770911490759637, 34.65506302916286,  29.35545217588892, 42.29577743856077]]],
    'GS': ['South Georgia and South Sandwich Islands', [[-38.298695, -60.327394, -25.181020, -53.817812]]],
    'GT': ['Guatemala', [[-92.2292486234, 13.7353376327, -88.2250227526, 17.8193260767]]],
    'GW': ['Guinea Bissau', [[-16.6774519516, 11.0404116887, -13.7004760401, 12.6281700708]]],
    'GY': ['Guyana', [[-61.4103029039, 1.26808828369, -56.5393857489, 8.36703481692]]],
    'HN': ['Honduras', [[-89.3533259753, 12.9846857772, -83.147219001, 16.0054057886]]],
    'HR': ['Croatia', [[13.3569755388, 42.47999136, 19.3904757016, 46.5037509222]]],
    'HT': ['Haiti', [[-74.4580336168, 18.0309927434, -71.6248732164, 20.5156839055]]],
    'HU': ['Hungary', [[16.2022982113, 45.7594811061, 22.710531447, 48.6238540716]]],
    'ID': ['Indonesia', [[95.2930261576, -10.3599874813, 141.03385176, 5.47982086834]]],
    'IE': ['Ireland', [[-9.97708574059, 51.3693012559, -5.03298539878, 55.5316222195]]],
    'IL': ['Israel', [[34.2654333839, 29.5013261988, 35.8363969256, 33.2774264593]]],
    'IM': ['Isle of Man', [[-4.850942, 54.039203, -4.296132, 54.423695]]],
    'IN': ['India', [[68.1766451354, 7.56553477623, 97.4025614766, 35.4940095078]]],
    'IQ': ['Iraq', [[38.7923405291, 29.0990251735, 48.5679712258, 37.3852635768]]],
    'IR': ['Iran', [[44.1092252948, 25.0782370061, 63.3166317076, 39.7130026312]]],
    'IS': ['Iceland', [[-25.3261840479, 60.2763829617, -12.609732225, 66.9267923041]]],
    'IT': ['Italy', [[6.6499552751, 36.519987291, 18.4802470232, 47.1153931748]]],
    'JE': ['Jersey', [[-2.255378, 49.160392, -2.003782, 49.262766]]],
    'JM': ['Jamaica', [[-78.4377192858, 17.7011162379, -76.1996585761, 18.5242184514]]],
    'JO': ['Jordan', [[34.9226025734, 29.1974946152, 39.1954683774, 33.3786864284]]],
    'JP': ['Japan', [[122.408463169, 24.0295791692, 145.543137242, 45.5514834662]]],
    'KE': ['Kenya', [[33.8935689697, -4.67677, 41.8550830926, 5.506]]],
    'KG': ['Kyrgyzstan', [[69.464886916, 39.2794632025, 80.2599902689, 43.2983393418]]],
    'KH': ['Cambodia', [[102.3480994, 10.4865436874, 107.614547968, 14.5705838078]]],
    'KI': ['Kiribati', [[-157.228370, -5.899120, -154.525674, 2.309838]]],
    'KM': ['Comoros', [[43.188474, -12.463598, 44.608457, -11.321376]]],
    'KN': ['Saint Kitts and Nevis', [[-62.870331, 17.093414, -62.527695, 17.431763]]],
    'KP': ['North Korea', [[124.265624628, 37.669070543, 130.780007359, 42.9853868678]]],
    'KR': ['South Korea', [[124.117397903, 33.3900458847, 129.468304478, 38.6122429469]]],
    'KW': ['Kuwait', [[46.5687134133, 28.5260627304, 48.4160941913, 30.0590699326]]],
    'KY': ['Cayman Islands', [[-82.464856, 19.182946, -79.613660, 19.825009]]],
    'KZ': ['Kazakhstan', [[46.4664457538, 40.6623245306, 87.3599703308, 55.3852501491]]],
    'LA': ['Laos', [[100.115987583, 13.88109101, 107.564525181, 22.4647531194]]],
    'LB': ['Lebanon', [[35.1260526873, 33.0890400254, 36.6117501157, 34.6449140488]]],
    'LC': ['St Lucia', [[-61.216819, 13.702059, -60.677914, 14.115870]]],
    'LI': ['Liechtenstein', [[9.455185, 47.046620, 9.629813, 47.275750]]],
    'LK': ['Sri Lanka', [[79.6951668639, 5.96836985923, 81.7879590189, 9.84407766361], [79.6444708682081, 9.470904842099836, 79.74474918772529, 9.555829147131542]]],
    'LR': ['Liberia', [[-11.4387794662, 4.35575511313, -7.53971513511, 8.54105520267]]],
    'LS': ['Lesotho', [[26.9992619158, -30.6451058896, 29.3251664568, -28.6475017229]]],
    'LT': ['Lithuania', [[21.0358004086, 53.9057022162, 26.5882792498, 56.3725283881]]],
    'LU': ['Luxembourg', [[5.67405195478, 49.4426671413, 6.54275109216, 50.1480516628]]],
    'LV': ['Latvia', [[21.0558004086, 55.61510692, 28.1767094256, 57.9701569688]]],
    'LY': ['Libya', [[9.31941084152, 19.58047, 25.16482, 33.1369957545]]],
    'MA': ['Morocco', [[-17.0204284327, 21.4207341578, -1.12455115397, 35.9999881048]]],
    'MC': ['Monaco', [[7.407828, 43.724330, 7.440444, 43.752297]]],
    'MD': ['Moldova', [[26.6193367856, 45.4882831895, 30.0246586443, 48.4671194525]]],
    'ME': ['Montenegro', [[18.45, 41.87755, 20.3398, 43.52384]]],
    'MF': ['Saint-Martin', [[-63.173560, 18.022431, -62.944875, 18.139666]]],
    'MG': ['Madagascar', [[43.2541870461, -25.6014344215, 50.4765368996, -12.0405567359]]],
    'MH': ['Marshall Island', [[161.842056, 3.845600, 172.740494, 10.814941]]],
    'MK': ['North Macedonia', [[20.46315, 40.8427269557, 22.9523771502, 42.3202595078]]],
    'ML': ['Mali', [[-12.1707502914, 10.0963607854, 4.27020999514, 24.9745740829]]],
    'MM': ['Myanmar', [[92.3032344909, 9.93295990645, 101.180005324, 28.335945136]]],
    'MN': ['Mongolia', [[87.7512642761, 41.5974095729, 119.772823928, 52.0473660345]]],
    'MQ': ['Martinique', [[-62.234232, 14.285308, -60.797525, 14.876946]]],
    'MR': ['Mauritania', [[-17.0634232243, 14.6168342147, -4.92333736817, 27.3957441269]]],
    'MS': ['Montserrat', [[-62.256975, 16.670934, -62.127199, 16.830380]]],
    'MT': ['Malta', [[14.166141, 35.715831, 15.590642, 36.081125]]],
    'MU': ['Mauritius', [[57.246428, -20.527530, 57.867156, -18.769458], [63.196815356054394, -19.83910465737219, 63.60345296734697, -19.62080881436224]]],
    'MV': ['Maldives', [[72.358411, -0.865774, 74.555676, 6.906712]]],
    'MW': ['Malawi', [[32.6881653175, -16.8012997372, 35.7719047381, -9.23059905359]]],
    'MX': ['Mexico', [[-119.12776, 14.5388286402, -86.491982388, 32.72083]]],
    'MY': ['Malaysia', [[99.085756871, 0.773131415201, 119.181903925, 6.92805288332]]],
    'MZ': ['Mozambique', [[30.1794812355, -26.7421916643, 40.7754752948, -10.3170960425]]],
    'NA': ['Namibia', [[11.7341988461, -29.045461928, 25.0844433937, -16.9413428687]]],
    'NC': ['New Caledonia', [[163.029605748, -23.3999760881, 168.120011428, -19.1056458473]]],
    'NE': ['Niger', [[0.295646396495, 11.6601671412, 15.9032466977, 23.4716684026]]],
    'NG': ['Nigeria', [[2.69170169436, 4.24059418377, 14.5771777686, 13.8659239771]]],
    'NI': ['Nicaragua', [[-87.6684934151, 10.7268390975, -83.147219001, 15.0162671981]]],
    'NL': ['Netherlands', [[3.31497114423, 50.803721015, 7.29205325687, 53.5104033474]]],
    'NO': ['Norway', [[4.99207807783, 57.0788841824, 31.29341841, 71.21311908]]],
    'NP': ['Nepal', [[80.0884245137, 26.3978980576, 88.1748043151, 30.4227169866]]],
    'NR': ['Nauru', [[166.9007475834, -0.5573764007, 166.9685492693, -0.4984335412]]],
    'NU': ['Niue', [[-169.954904, -19.160813, -169.762987, -18.948258]]],
    'NZ': ['New Zealand', [[166.309144322, -46.641235447, 178.517093541, -34.4506617165]]],
    'OM': ['Oman', [[52.0000098, 16.6510511337, 59.8080603372, 26.3959343531]]],
    'PA': ['Panama', [[-82.9657830472, 6.9205414901, -77.2425664944, 9.61161001224]]],
    'PE': ['Peru', [[-81.6109425524, -18.3479753557, -68.6650797187, -0.0572054988649]]],
    'PG': ['Papua New Guinea', [[141.000210403, -10.6524760881, 156.019965448, -2.50000212973]]],
    'PH': ['Philippines', [[117.17427453, 5.58100332277, 126.537423944, 20.5052273625]]],
    'PK': ['Pakistan', [[60.8742484882, 23.6919650335, 77.8374507995, 37.1330309108]]],
    'PL': ['Poland', [[14.0745211117, 49.0273953314, 24.0299857927, 54.8515359564]]],
    'PR': ['Puerto Rico', [[-67.2424275377, 17.946553453, -65.5910037909, 18.5206011011]]],
    'PS': ['West Bank', [[34.9274084816, 31.3534353704, 35.5456653175, 32.5325106878]]],
    'PS': ['Palestine', [[34.161353, 31.036574, 35.864234, 32.824322]]],
    'PT': ['Portugal', [[-11.72657060387, 36.838268541, -6.3890876937, 42.280468655], [-17.451724962564013, 31.401532401650364, -16.048078338508628, 33.13531220458579], [-32.47751352524867, 36.137579870831885, -21.469213296357385, 40.763624391184145]]],
    'PY': ['Paraguay', [[-62.6850571357, -27.5484990374, -54.2929595608, -19.3427466773]]],
    'QA': ['Qatar', [[50.7439107603, 24.5563308782, 52.6067004738, 26.1145820175]]],
    'RE': ['Reunion', [[54.206600, -21.375728, 56.356996, -20.667645]]],
    'RO': ['Romania', [[20.2201924985, 43.6884447292, 29.62654341, 48.2208812526]]],
    'RS': ['Serbia', [[18.82982, 42.2452243971, 22.9860185076, 46.1717298447]]],
    'RU': ['Russia', [[26.822680, 40.483493, 180, 81.903807], [-180, 61, -169, 72], [19.489414671469504, 54.33182221678806, 22.905639654213825, 55.31413673335722]]],
    'RW': ['Rwanda', [[29.0249263852, -2.91785776125, 30.8161348813, -1.13465911215]]],
    'SA': ['Saudi Arabia', [[34.6323360532, 16.3478913436, 55.6666593769, 32.161008816]]],
    'SB': ['Solomon Islands', [[155.391357864, -10.8263672828, 162.398645868, -6.49933847415]]],
    'SC': ['Seychelles', [[55.174998, -4.822535, 56.007276, -3.546368]]],
    'SD': ['Sudan', [[21.93681, 8.61972971293, 38.4100899595, 22.0], [31.309568631189364, 22.0, 31.51105877462657, 22.228282131067726]]],
    'SE': ['Sweden', [[10.0273686052, 55.2617373725, 24.9033785336, 69.1062472602]]],
    'SG': ['Singapore', [[103.570233, 1.158152, 104.097863, 1.468348]]],
    'SH': ['Saint Helena', [[-15.8169342584, -38.0372386419, -5.6134693669, -11.8971012947]]],
    'SI': ['Slovenia', [[13.367471, 45.418064, 16.618664, 46.884908]]],
    'SK': ['Slovakia', [[16.8799829444, 47.7484288601, 22.5581376482, 49.5715740017]]],
    'SL': ['Sierra Leone', [[-13.2465502588, 6.78591685631, -10.2300935531, 10.0469839543]]],
    'SM': ['San Marino', [[12.401383, 43.893395, 12.521954, 43.993838]]],
    'SN': ['Senegal', [[-17.6250426905, 12.332089952, -11.4678991358, 16.5982636581]]],
    'SO': ['Somalia', [[40.98105, -1.68325, 51.13387, 12.02464]]],
    'SR': ['Suriname', [[-58.0446943834, 1.81766714112, -53.9580446031, 6.0252914494]]],
    'SS': ['South Sudan', [[23.8869795809, 3.50917, 35.2980071182, 12.2480077571]]],
    'ST': ['Sao Tome and Principe', [[6.372594, -0.065411, 6.790074, 0.439956]]],
    'SV': ['El Salvador', [[-90.0955545723, 13.1490168319, -87.7235029772, 14.4241327987]]],
    'SX': ['Sint Maarten', [[-63.160383, 17.909370, -63.003557, 18.063344]]],
    'SY': ['Syria', [[35.7007979673, 32.312937527, 42.3495910988, 37.2298725449]]],
    'SZ': ['Eswatini', [[30.6766085141, -27.2858794085, 32.0716654803, -25.660190525]]],
    'TC': ['Turks and Caicos Islands', [[-72.515351, 21.176436, -71.111847, 21.973323]]],
    'TD': ['Chad', [[13.5403935076, 7.42192454674, 23.88689, 23.40972]]],
    'TF': ['Fr. S. and Antarctic Lands', [[68.72, -49.775, 70.56, -48.625]]],
    'TG': ['Togo', [[-0.0497847151599, 5.92883738853, 1.86524051271, 11.0186817489]]],
    'TH': ['Thailand', [[97.3758964376, 5.69138418215, 105.589038527, 20.4178496363]]],
    'TJ': ['Tajikistan', [[67.4422196796, 36.7381712916, 74.9800024759, 40.9602133245]]],
    'TK': ['Tokelau', [[-172.534264, -9.492260, -171.059350, -8.485807]]],
    'TL': ['East Timor', [[124.968682489, -9.39317310958, 127.335928176, -8.27334482181]]],
    'TM': ['Turkmenistan', [[52.5024597512, 35.2706639674, 66.5461503437, 42.7515510117]]],
    'TN': ['Tunisia', [[7.52448164229, 30.3075560572, 11.4887874691, 37.3499944118]]],
    'TO': ['Tonga', [[-176.986604, -22.027399, -173.069058, -15.410732]]],
    'TR': ['Turkey', [[25.60417275656444, 35.27139944988264, 47.7939896991, 42.1414848903]]],
    'TT': ['Trinidad and Tobago', [[-61.95, 10.0, -60.895, 10.89]]],
    'TV': ['Tuvalu', [[175.014362906, -11.134731836, 180, -5.002830727]]],
    'TW': ['Taiwan', [[120.106188593, 21.9705713974, 121.951243931, 26.2954588893]]],
    'TZ': ['Tanzania', [[29.3399975929, -11.7209380022, 40.31659, -0.95]]],
    'UA': ['Ukraine', [[22.0856083513, 44.2614785833, 40.0807890155, 52.3350745713]]],
    'UG': ['Uganda', [[29.5794661801, -1.44332244223, 35.03599, 4.24988494736]]],
    'US': ['United States', [[-127.60300365652778, 23.328307850864494, -64.80508473115059, 49.1844355407274], [-160.82810044701534, 18.30244581034809, -153.59304286436185, 22.489114511005596], [-190.60787503833, 50.95801418800582, -130.4491456421077, 71.56926153367206]]],
    'UY': ['Uruguay', [[-58.4270741441, -35.0526465797, -53.209588996, -30.1096863746]]],
    'UZ': ['Uzbekistan', [[55.9289172707, 37.1449940049, 73.055417108, 45.5868043076]]],
    'VA': ['Vatican City', [[12.445713,41.900179,12.458437,41.9074918]]],
    'VC': ['St Vincent and the Grenadines', [[-61.488755, 12.513980, -61.104166, 13.597771]]],
    'VE': ['Venezuela', [[-73.3049515449, 0.724452215982, -59.7582848782, 12.1623070337]]],
    'VG': ['British Virgin Islands', [[-64.862530, 18.300936, -64.262402, 18.759272]]],
    'VN': ['Vietnam', [[102.170435826, 8.59975962975, 109.33526981, 23.3520633001]]],
    'VU': ['Vanuatu', [[165.77076852020062, -20.465046828827884, 170.84645193920196, -12.744244960446533]]],
    'WS': ['Samoa', [[-172.850164, -14.081769, -171.309332, -13.404114]]],
    'XK': ['Kosovo', [[20.023050, 41.851277, 21.791849, 43.271330]]],
    'YE': ['Yemen', [[42.6048726743, 12.5859504257, 53.1085726255, 19.0000033635]]],
    'YT': ['Mayotte', [[44.005064, -13.012022, 45.319548, -11.631733]]],
    'ZA': ['South Africa', [[16.3449768409, -34.8191663551, 32.830120477, -22.0913127581]]],
    'ZM': ['Zambia', [[21.887842645, -17.9612289364, 33.4856876971, -8.23825652429]]],
    'ZW': ['Zimbabwe', [[25.2642257016, -22.2716118303, 32.8498608742, -15.5077869605]]],
    'SJ': ['Svalbard', [[10.04687789766614, 74.35498023304599, 34.306805275624086, 80.81809323746566]]],
    'AS': ['American Samoa', [[-170.8610098435224, -14.38536238983563, -170.5262297667812, -14.226237921088725]]],
    'BL': ['Saint Barthelemy', [[-62.920134746383596, 17.874249226856882, -62.781361781310444, 17.962748324810512]]],
    'PW': ['Palau', [[130.85241878355825, 2.276788844461931, 135.76330741590354, 8.605929299211784]]],
    'GU': ['Guam', [[144.37910069285803, 13.074077183069257, 145.2219837083251, 13.871093966229127]]],
    'NF': ['Norfolk Island', [[167.88255366736797, -29.154067146012604, 168.04076064851756, -28.96378963203278]]],
    'AX': ['Aland Islands', [[19.41546265377435, 59.89282758281474, 21.155608234093492, 60.61358224907711]]],
    'PF': ['French Polynesia', [[-152.8492413037696, -18.504696574791765, -136.457641544589, -7.824286674613189]]],
    'WW': ['Worldwide', [[-160, -20, 180, 60]]]
}

codes_dict = {
  'Aruba': 'AW',
  'Congo-Brazzaville': 'CG',
  'Curacao': 'CW',
  'Bonaire, Sint Eustatius, and Saba': 'BQ',
  'Saint Helena, Ascension and Tristan da Cunha': 'SH',
  'American Samoa': 'AS',
  'Saint Lucia': 'LC',
  'Saint Vincent and the Grenadines': 'VC',
  'St Vincent and Grenadines': 'VC',
  'Svalbard and Jan Mayen': 'SJ',
  'Réunion': 'RE',
  'Czechia': 'CZ',
  'Northern Cyprus': 'TY', # 'TY' is an unassigned ISO code
  'The Netherlands': 'NL',
  'Palestinian Territory': 'PS',
  'Abkhazia': 'GE',
  'Åland': 'AX',
  'Türkiye': 'TR',
  'Côte d\'Ivoire': 'CI',
  'South Georgia and the South Sandwich Islands': 'GS',
  'Federated States of Micronesia': 'FM'
}

latitude_dict = {
  -90: {'AQ'},
  -89: {'AQ'},
  -88: {'AQ'},
  -87: {'AQ'},
  -86: {'AQ'},
  -85: {'AQ'},
  -84: {'AQ'},
  -83: {'AQ'},
  -82: {'AQ'},
  -81: {'AQ'},
  -80: {'AQ'},
  -79: {'AQ'},
  -78: {'AQ'},
  -77: {'AQ'},
  -76: {'AQ'},
  -75: {'AQ'},
  -74: {'AQ'},
  -73: {'AQ'},
  -72: {'AQ'},
  -71: {'AQ'},
  -70: {'AQ'},
  -69: {'AQ'},
  -68: {'AQ'},
  -67: {'AQ'},
  -66: {'AQ'},
  -65: {'AQ'},
  -64: {'AQ'},
  -63: {'AQ'},
  -62: {'AQ'},
  -61: {'AQ'},
  -60: {''},
  -59: {'GS'},
  -58: {'GS'},
  -57: {'GS', 'CL'},
  -56: {'GS', 'CL', 'AR'},
  -55: {'GS', 'CL', 'AR'},
  -54: {'GS', 'CL', 'FK', 'AR'},
  -53: {'CL', 'FK', 'AR'},
  -52: {'NZ', 'CL', 'FK', 'AR'},
  -51: {'TF', 'FK', 'NZ', 'AR', 'CL', 'FR'},
  -50: {'TF', 'CL', 'AR', 'FR'},
  -49: {'TF', 'CL', 'AR', 'FR'},
  -48: {'NZ', 'ZA', 'CL', 'AR', 'FR'},
  -47: {'NZ', 'ZA', 'CL', 'AR', 'FR'},
  -46: {'NZ', 'CL', 'AR', 'FR'},
  -45: {'NZ', 'CL', 'AR'},
  -44: {'AU', 'NZ', 'CL', 'AR'},
  -43: {'AU', 'NZ', 'CL', 'AR'},
  -42: {'AU', 'NZ', 'CL', 'AR'},
  -41: {'AU', 'NZ', 'CL', 'AR'},
  -40: {'AU', 'NZ', 'CL', 'AR'},
  -39: {'AU', 'NZ', 'CL', 'AR'},
  -38: {'AU', 'NZ', 'CL', 'AR'},
  -37: {'AU', 'NZ', 'CL', 'AR'},
  -36: {'AU', 'NZ', 'ZA', 'AR', 'CL', 'UY'},
  -35: {'AU', 'NZ', 'ZA', 'AR', 'CL', 'UY'},
  -34: {'AU', 'NZ', 'ZA', 'AR', 'CL', 'UY'},
  -33: {'AU', 'ZA', 'AR', 'CL', 'BR', 'UY'},
  -32: {'AU', 'ZA', 'AR', 'CL', 'BR', 'UY'},
  -31: {'AU', 'LS', 'ZA', 'AR', 'CL', 'BR', 'UY'},
  -30: {'AU', 'LS', 'ZA', 'AR', 'CL', 'BR'},
  -29: {'AU', 'LS', 'ZA', 'AR', 'NA', 'CL', 'BR'},
  -28: {'AU', 'ZA', 'AR', 'NA', 'CL', 'PY', 'BR', 'SZ'},
  -27: {'AU', 'MZ', 'BW', 'ZA', 'AR', 'NA', 'CL', 'PY', 'BR', 'SZ'},
  -26: {'AU', 'MG', 'MZ', 'BW', 'ZA', 'AR', 'NA', 'CL', 'PY', 'BR', 'SZ'},
  -25: {'AU', 'MG', 'MZ', 'BW', 'TO', 'ZA', 'AR', 'NA', 'CL', 'PY', 'BR'},
  -24: {'AU', 'MG', 'MZ', 'BW', 'TO', 'ZA', 'AR', 'NA', 'CL', 'PY', 'BR', 'FR'},
  -23: {'AU', 'MG', 'NC', 'MZ', 'BW', 'TO', 'ZA', 'AR', 'ZW', 'NA', 'CL', 'PY', 'BR', 'FR', 'BO', 'CK'},
  -22: {'AU', 'MG', 'NC', 'FJ', 'MZ', 'BW', 'TO', 'RE', 'AR', 'ZW', 'NA', 'CL', 'PY', 'BR', 'FR', 'BO', 'CK'},
  -21: {'AU', 'MG', 'VU', 'MZ', 'FJ', 'BW', 'NC', 'TO', 'RE', 'ZW', 'NA', 'CL', 'PY', 'MU', 'BR', 'FR', 'BO', 'CK'},
  -20: {'AU', 'MG', 'VU', 'MZ', 'FJ', 'BW', 'NC', 'TO', 'ZW', 'NA', 'CL', 'PE', 'PY', 'MU', 'BR', 'FR', 'BO', 'NU', 'CK'},
  -19: {'AU', 'MG', 'VU', 'MZ', 'FJ', 'BW', 'TO', 'ZW', 'NA', 'CL', 'PE', 'BR', 'FR', 'BO', 'NU', 'CK'},
  -18: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'BW', 'AO', 'FJ', 'TO', 'KN', 'ZW', 'NA', 'PE', 'BR', 'FR', 'BO', 'CK'},
  -17: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'AO', 'FJ', 'TO', 'ZW', 'NA', 'PE', 'MW', 'BR', 'FR', 'BO'},
  -16: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'AO', 'FJ', 'TO', 'ZW', 'PE', 'MW', 'BR', 'FR', 'BO'},
  -15: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'AO', 'WS', 'PE', 'MW', 'BR', 'FR', 'BO'},
  -14: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'AO', 'CD', 'WS', 'PE', 'MW', 'BR', 'FR', 'BO'},
  -13: {'AU', 'ZM', 'MG', 'VU', 'MZ', 'AO', 'CD', 'SB', 'KM', 'PE', 'MW', 'BR', 'FR', 'BO'},
  -12: {'AU', 'ZM', 'MG', 'MZ', 'AO', 'CD', 'SB', 'KM', 'PE', 'MW', 'PG', 'ID', 'BR', 'FR', 'BO', 'TZ', 'CK'},
  -11: {'AU', 'ZM', 'MZ', 'AO', 'CD', 'SB', 'SC', 'PE', 'MW', 'KI', 'PG', 'ID', 'BR', 'FR', 'BO', 'TZ', 'CK'},
  -10: {'ZM', 'AO', 'ID', 'CD', 'SB', 'SC', 'PE', 'TK', 'MW', 'KI', 'PG', 'TL', 'BR', 'FR', 'BO', 'TZ', 'CK'},
  -9: {'ZM', 'AO', 'ID', 'CD', 'SB', 'PE', 'TK', 'TL', 'BR', 'FR', 'PG', 'TZ', 'CK'},
  -8: {'AO', 'CD', 'SB', 'PE', 'ID', 'BR', 'PG', 'TZ'},
  -7: {'AO', 'CD', 'SB', 'SC', 'PE', 'ID', 'BR', 'PG', 'TZ'},
  -6: {'AO', 'CD', 'SC', 'PE', 'CG', 'ID', 'BR', 'PG', 'TZ'},
  -5: {'GA', 'CD', 'CO', 'BI', 'CG', 'PE', 'EC', 'KE', 'ID', 'BR', 'KI', 'PG', 'TZ'},
  -4: {'GA', 'CD', 'CO', 'BI', 'CG', 'PE', 'EC', 'KE', 'ID', 'BR', 'KI', 'PG', 'TZ'},
  -3: {'GA', 'CD', 'CO', 'BI', 'CG', 'PE', 'EC', 'KE', 'RW', 'ID', 'BR', 'KI', 'PG', 'TZ'},
  -2: {'GA', 'CD', 'CO', 'SO', 'CG', 'PE', 'EC', 'UG', 'KE', 'RW', 'ID', 'BR', 'PG', 'TZ'},
  -1: {'GA', 'MV', 'CD', 'CO', 'SO', 'CG', 'PE', 'EC', 'UG', 'KE', 'ID', 'BR', 'PG', 'TZ'},
  0: {'ST', 'GA', 'MV', 'CD', 'CO', 'VE', 'SO', 'CG', 'EC', 'UG', 'KE', 'FM', 'ID', 'BR', 'KI'},
  1: {'ST', 'GA', 'GY', 'SR', 'MV', 'CD', 'CM', 'VE', 'SO', 'CO', 'SG', 'CG', 'EC', 'UG', 'GQ', 'KE', 'FM', 'ID', 'BR', 'KI', 'MY'},
  2: {'KE', 'GA', 'GY', 'SR', 'MV', 'CD', 'CO', 'SO', 'CM', 'VE', 'CG', 'UG', 'GQ', 'KI', 'ID', 'BR', 'FR', 'FM', 'MY'},
  3: {'ET', 'KE', 'GY', 'SR', 'SS', 'CD', 'CO', 'SO', 'CM', 'MV', 'VE', 'CF', 'CG', 'UG', 'KI', 'ID', 'BR', 'FR', 'FM', 'MY'},
  4: {'ET', 'GY', 'UG', 'FM', 'BR', 'SR', 'CD', 'CO', 'SO', 'BN', 'CM', 'SS', 'MV', 'VE', 'CI', 'ID', 'GH', 'MY', 'PH', 'NG', 'CF', 'KE', 'FR', 'LR'},
  5: {'ET', 'GY', 'FM', 'SR', 'CD', 'CO', 'SO', 'BN', 'CM', 'SS', 'MV', 'LK', 'VE', 'CI', 'GH', 'ID', 'MY', 'PH', 'NG', 'MH', 'CF', 'FR', 'LR'},
  6: {'ET', 'GY', 'SL', 'FM', 'SR', 'CM', 'CO', 'SO', 'BJ', 'TG', 'SS', 'IN', 'MV', 'LK', 'VE', 'CI', 'GH', 'ID', 'MY', 'PH', 'NG', 'MH', 'CF', 'LR', 'TH'},
  7: {'ET', 'GY', 'SL', 'FM', 'CM', 'CO', 'SO', 'BJ', 'TG', 'SS', 'IN', 'PA', 'LK', 'MV', 'VE', 'CI', 'GN', 'GH', 'MY', 'PH', 'NG', 'CR', 'MH', 'CF', 'TD', 'LR', 'TH'},
  8: {'ET', 'SD', 'GY', 'SL', 'FM', 'VN', 'CM', 'CO', 'SO', 'BJ', 'TG', 'SS', 'IN', 'PA', 'LK', 'VE', 'CI', 'GN', 'GH', 'PH', 'NG', 'CR', 'MH', 'CF', 'TD', 'LR', 'TH'},
  9: {'ET', 'SD', 'SL', 'VN', 'KH', 'CM', 'CO', 'BJ', 'SO', 'TG', 'BF', 'SS', 'IN', 'PA', 'LK', 'TT', 'VE', 'CI', 'GN', 'GH', 'PH', 'NG', 'MM', 'CR', 'MH', 'CF', 'TD', 'FM', 'TH'},
  10: {'ET', 'SD', 'VN', 'KH', 'CM', 'CO', 'BJ', 'SO', 'TG', 'NI', 'BF', 'DJ', 'SS', 'IN', 'LK', 'ML', 'TT', 'VE', 'CI', 'GN', 'GH', 'GW', 'PH', 'NG', 'MM', 'CR', 'MH', 'CF', 'TD', 'FM', 'TH'},
  11: {'ET', 'SD', 'YE', 'VN', 'KH', 'CM', 'CO', 'SO', 'BJ', 'NI', 'GD', 'BF', 'DJ', 'SS', 'IN', 'ML', 'TT', 'VE', 'GN', 'GH', 'NL', 'GW', 'PH', 'NG', 'MM', 'MH', 'TD', 'TH'},
  12: {'ET', 'SD', 'YE', 'NE', 'VN', 'KH', 'CM', 'CO', 'SO', 'SN', 'BJ', 'NI', 'GD', 'BF', 'DJ', 'SS', 'IN', 'ML', 'VE', 'BB', 'GN', 'NL', 'VC', 'GW', 'PH', 'NG', 'MM', 'TD', 'ER', 'TH'},
  13: {'ET', 'SD', 'GM', 'YE', 'NE', 'VN', 'KH', 'CO', 'SN', 'HN', 'NI', 'GT', 'BF', 'IN', 'ML', 'LA', 'BB', 'SV', 'VC', 'PH', 'NG', 'MM', 'LC', 'TD', 'ER', 'TH'},
  14: {'ET', 'SD', 'YE', 'NE', 'VN', 'KH', 'MR', 'CO', 'SN', 'HN', 'NI', 'CV', 'GT', 'BF', 'IN', 'ML', 'LA', 'SV', 'DM', 'PH', 'MM', 'LC', 'TD', 'ER', 'TH', 'FR'},
  15: {'SD', 'YE', 'NE', 'VN', 'MR', 'SN', 'HN', 'CV', 'GT', 'ER', 'IN', 'ML', 'LA', 'DM', 'CN', 'PH', 'BZ', 'MM', 'TD', 'FR', 'TH', 'MX'},
  16: {'JM', 'SD', 'YE', 'NE', 'VN', 'AG', 'MR', 'SN', 'HN', 'OM', 'CV', 'GT', 'IN', 'ML', 'SA', 'LA', 'CN', 'PH', 'BZ', 'MM', 'FR', 'TD', 'ER', 'TH', 'MX'},
  17: {'JM', 'SD', 'DO', 'YE', 'NE', 'VN', 'AG', 'HT', 'MR', 'OM', 'CV', 'GT', 'IN', 'ML', 'SA', 'LA', 'PR', 'NL', 'PH', 'BZ', 'MM', 'TD', 'ER', 'TH', 'MX'},
  18: {'JM', 'SD', 'DO', 'YE', 'NE', 'VN', 'VG', 'HT', 'MR', 'OM', 'IN', 'ML', 'SA', 'LA', 'PR', 'NL', 'PH', 'BZ', 'MM', 'TD', 'US', 'TH', 'MX'},
  19: {'DZ', 'CN', 'SD', 'MR', 'IN', 'PH', 'ML', 'MM', 'SA', 'OM', 'DO', 'LY', 'LA', 'CU', 'NE', 'TD', 'VN', 'US', 'HT', 'TH', 'MX'},
  20: {'SD', 'BS', 'DO', 'LY', 'NE', 'VN', 'HT', 'MR', 'OM', 'DZ', 'IN', 'ML', 'SA', 'LA', 'CU', 'CN', 'PH', 'MM', 'TD', 'US', 'TH', 'MX'},
  21: {'SD', 'BD', 'BS', 'DO', 'LY', 'NE', 'VN', 'MR', 'OM', 'DZ', 'IN', 'ML', 'SA', 'TW', 'EG', 'EH', 'LA', 'CU', 'TC', 'CN', 'PH', 'MM', 'TD', 'US', 'MX'},
  22: {'SD', 'BD', 'BS', 'LY', 'NE', 'VN', 'MR', 'OM', 'DZ', 'IN', 'ML', 'SA', 'TW', 'EG', 'EH', 'LA', 'AE', 'CU', 'TC', 'CN', 'MM', 'TD', 'US', 'MX'},
  23: {'BD', 'JP', 'BS', 'LY', 'NE', 'VN', 'MR', 'OM', 'DZ', 'IN', 'ML', 'SA', 'TW', 'EG', 'EH', 'AE', 'CU', 'CN', 'MM', 'TD', 'PK', 'US', 'MX'},
  24: {'BD', 'JP', 'BS', 'LY', 'QA', 'IR', 'MR', 'OM', 'DZ', 'IN', 'ML', 'SA', 'TW', 'EG', 'EH', 'AE', 'CN', 'MM', 'PK', 'US', 'MX'},
  25: {'DZ', 'IR', 'CN', 'MR', 'BD', 'JP', 'IN', 'ML', 'MM', 'BS', 'SA', 'TW', 'EG', 'EH', 'AE', 'LY', 'PK', 'QA', 'US', 'MX'},
  26: {'BD', 'JP', 'BS', 'LY', 'QA', 'IR', 'MR', 'DZ', 'IN', 'SA', 'TW', 'EG', 'EH', 'AE', 'CN', 'MM', 'BT', 'PK', 'NP', 'US', 'MX'},
  27: {'DZ', 'IR', 'CN', 'ES', 'JP', 'IN', 'MM', 'BS', 'SA', 'EG', 'BT', 'LY', 'PK', 'NP', 'US', 'MX'},
  28: {'DZ', 'IR', 'CN', 'ES', 'JP', 'IN', 'MM', 'SA', 'EG', 'BT', 'MA', 'LY', 'PK', 'NP', 'US', 'KW', 'MX'},
  29: {'DZ', 'IR', 'CN', 'ES', 'JP', 'IN', 'AF', 'PT', 'JO', 'SA', 'IL', 'EG', 'LY', 'MA', 'PK', 'NP', 'IQ', 'QA', 'US', 'KW', 'MX'},
  30: {'DZ', 'IR', 'CN', 'AF', 'JP', 'IN', 'TN', 'PT', 'JO', 'SA', 'IL', 'EG', 'MA', 'LY', 'PK', 'NP', 'IQ', 'QA', 'US', 'MX'},
  31: {'DZ', 'IR', 'PS', 'CN', 'AF', 'JP', 'IN', 'TN', 'PT', 'JO', 'SA', 'IL', 'EG', 'MA', 'LY', 'PK', 'IQ', 'US', 'MX'},
  32: {'DZ', 'IR', 'PS', 'CN', 'AF', 'JP', 'IN', 'TN', 'SY', 'PT', 'JO', 'SA', 'IL', 'LY', 'MA', 'PK', 'IQ', 'US'},
  33: {'KR', 'DZ', 'IR', 'CN', 'AF', 'JP', 'IN', 'TN', 'SY', 'PT', 'IL', 'MA', 'LY', 'PK', 'IQ', 'LB', 'US'},
  34: {'KR', 'DZ', 'IR', 'GR', 'CN', 'AF', 'JP', 'IN', 'TN', 'SY', 'CY', 'MA', 'PK', 'IQ', 'LB', 'US'},
  35: {'KR', 'DZ', 'IR', 'GR', 'CN', 'ES', 'JP', 'IT', 'SY', 'IN', 'AF', 'TN', 'IQ', 'CY', 'MA', 'TR', 'PK', 'GI', 'US', 'MT', 'TM'},
  36: {'KR', 'DZ', 'IR', 'GR', 'CN', 'ES', 'JP', 'IT', 'SY', 'PT', 'AF', 'TN', 'IQ', 'TR', 'TJ', 'PK', 'GI', 'US', 'MT', 'TM'},
  37: {'KR', 'DZ', 'IR', 'GR', 'KP', 'ES', 'JP', 'IT', 'TN', 'SY', 'PT', 'CN', 'AF', 'UZ', 'TJ', 'TR', 'IQ', 'US', 'TM'},
  38: {'KR', 'GR', 'IR', 'KP', 'CN', 'AF', 'JP', 'ES', 'IT', 'PT', 'AZ', 'UZ', 'TJ', 'TR', 'US', 'TM'},
  39: {'KP', 'AL', 'IR', 'GR', 'CN', 'ES', 'JP', 'IT', 'AZ', 'PT', 'KG', 'AM', 'UZ', 'TJ', 'TR', 'US', 'TM'},
  40: {'KP', 'AL', 'CN', 'GR', 'ES', 'JP', 'IT', 'AZ', 'PT', 'KG', 'MK', 'AM', 'UZ', 'TJ', 'TR', 'US', 'TM'},
  41: {'AL', 'ES', 'JP', 'AZ', 'VA', 'MK', 'GE', 'KP', 'IT', 'PT', 'KG', 'UZ', 'MN', 'BG', 'ME', 'AD', 'TM', 'GR', 'CN', 'KZ', 'AM', 'TR', 'US', 'FR'},
  42: {'AL', 'ES', 'JP', 'VA', 'MK', 'HR', 'GE', 'XK', 'KP', 'RS', 'IT', 'KG', 'CA', 'UZ', 'BA', 'MN', 'BG', 'ME', 'AD', 'RU', 'TM', 'CN', 'KZ', 'TR', 'US', 'FR'},
  43: {'RO', 'CN', 'RS', 'ES', 'JP', 'IT', 'KZ', 'RU', 'KG', 'MC', 'CA', 'HR', 'UZ', 'BA', 'ME', 'MN', 'US', 'GE', 'BG', 'XK', 'FR'},
  44: {'RO', 'UA', 'CN', 'RS', 'IT', 'JP', 'KZ', 'RU', 'CA', 'HR', 'UZ', 'BA', 'MN', 'US', 'FR', 'BG'},
  45: {'HU', 'RO', 'CN', 'UA', 'RS', 'JP', 'IT', 'KZ', 'RU', 'CA', 'CH', 'UZ', 'SI', 'BA', 'MN', 'HR', 'US', 'FR'},
  46: {'HU', 'RO', 'CN', 'UA', 'RS', 'IT', 'KZ', 'RU', 'CA', 'HR', 'SI', 'CH', 'MD', 'MN', 'AT', 'US', 'FR'},
  47: {'HU', 'RO', 'CN', 'UA', 'IT', 'KZ', 'RU', 'MN', 'CA', 'DE', 'CH', 'MD', 'SK', 'AT', 'US', 'FR'},
  48: {'HU', 'RO', 'CN', 'UA', 'US', 'KZ', 'RU', 'MN', 'JE', 'CA', 'DE', 'MD', 'SK', 'AT', 'CZ', 'FR'},
  49: {'BE', 'LU', 'CN', 'UA', 'KZ', 'RU', 'PL', 'GG', 'MN', 'JE', 'CA', 'GB', 'DE', 'SK', 'AT', 'CZ', 'FR'},
  50: {'BE', 'LU', 'CN', 'UA', 'KZ', 'RU', 'PL', 'CA', 'GB', 'DE', 'MN', 'CZ', 'FR'},
  51: {'BE', 'CN', 'UA', 'KZ', 'RU', 'PL', 'CA', 'GB', 'DE', 'IE', 'MN', 'CZ', 'FR', 'NL', 'BY'},
  52: {'UA', 'CN', 'KZ', 'RU', 'PL', 'CA', 'GB', 'DE', 'IE', 'MN', 'US', 'NL', 'BY'},
  53: {'KZ', 'RU', 'PL', 'CA', 'GB', 'DE', 'IE', 'LT', 'US', 'NL', 'IM', 'BY'},
  54: {'KZ', 'RU', 'PL', 'CA', 'DK', 'GB', 'DE', 'IE', 'US', 'LT', 'IM', 'BY'},
  55: {'KZ', 'RU', 'PL', 'CA', 'LV', 'GB', 'DE', 'IE', 'DK', 'US', 'SE', 'LT', 'BY'},
  56: {'RU', 'CA', 'LV', 'GB', 'DK', 'US', 'SE', 'LT', 'BY'},
  57: {'RU', 'NO', 'CA', 'LV', 'GB', 'US', 'SE', 'EE', 'DK'},
  58: {'RU', 'NO', 'CA', 'LV', 'GB', 'US', 'SE', 'EE'},
  59: {'GL', 'RU', 'NO', 'CA', 'GB', 'FI', 'US', 'SE', 'EE'},
  60: {'GL', 'RU', 'NO', 'CA', 'GB', 'FI', 'US', 'SE'},
  61: {'US', 'GL', 'RU', 'NO', 'CA', 'FI', 'GB', 'FO', 'SE'},
  62: {'US', 'GL', 'RU', 'NO', 'CA', 'FI', 'FO', 'SE'},
  63: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE', 'IS'},
  64: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE', 'IS'},
  65: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE', 'IS'},
  66: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE', 'IS'},
  67: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE', 'IS'},
  68: {'GL', 'RU', 'NO', 'CA', 'FI', 'US', 'SE'},
  69: {'GL', 'NO', 'RU', 'CA', 'FI', 'US'},
  70: {'GL', 'NO', 'RU', 'CA', 'FI', 'US'},
  71: {'NO', 'RU', 'CA', 'GL'},
  72: {'RU', 'CA', 'GL'},
  73: {'RU', 'CA', 'GL'},
  74: {'SJ', 'RU', 'CA', 'GL'},
  75: {'SJ', 'RU', 'CA', 'GL'},
  76: {'SJ', 'RU', 'CA', 'GL'},
  77: {'SJ', 'RU', 'CA', 'GL'},
  78: {'SJ', 'RU', 'CA', 'GL'},
  79: {'SJ', 'RU', 'CA', 'GL'},
  80: {'SJ', 'RU', 'CA', 'GL'},
  81: {'SJ', 'RU', 'CA', 'GL'},
  82: {'CA', 'GL'},
  83: {''},
  84: {''},
  85: {''},
  86: {''},
  87: {''},
  88: {''},
  89: {''},
  90: {''}
}

longitude_dict = {
  -179: {'RU', 'US', 'AQ', 'FJ', 'TO'},
  -178: {'RU', 'US', 'AQ', 'NZ'},
  -177: {'RU', 'US', 'AQ', 'NZ'},
  -176: {'RU', 'US', 'TO', 'AQ', 'NZ'},
  -175: {'RU', 'US', 'AQ', 'TO'},
  -174: {'RU', 'US', 'AQ', 'TO'},
  -173: {'RU', 'TK', 'WS', 'AQ'},
  -172: {'RU', 'KI', 'TK', 'WS', 'AQ'},
  -171: {'NU', 'RU', 'US', 'AQ', 'KI'},
  -170: {'RU', 'US', 'AQ', 'NU'},
  -169: {'US', 'AQ'},
  -168: {'US', 'AQ'},
  -167: {'US', 'AQ', 'CK'},
  -166: {'US', 'AQ', 'CK'},
  -165: {'US', 'AQ', 'CK'},
  -164: {'US', 'AQ', 'CK'},
  -163: {'US', 'AQ', 'CK'},
  -162: {'US', 'AQ', 'CK'},
  -161: {'US', 'AQ', 'CK'},
  -160: {'US', 'AQ', 'CK'},
  -159: {'US', 'AQ', 'CK'},
  -158: {'US', 'AQ', 'CK'},
  -157: {'US', 'AQ'},
  -156: {'US', 'AQ', 'KI'},
  -155: {'US', 'FR', 'AQ', 'KI'},
  -154: {'US', 'FR', 'AQ'},
  -153: {'US', 'FR', 'AQ'},
  -152: {'US', 'FR', 'AQ'},
  -151: {'US', 'FR', 'AQ', 'KI'},
  -150: {'US', 'FR', 'AQ', 'KI'},
  -149: {'US', 'FR', 'AQ'},
  -148: {'US', 'FR', 'AQ'},
  -147: {'US', 'FR', 'AQ'},
  -146: {'US', 'FR', 'AQ'},
  -145: {'US', 'FR', 'AQ'},
  -144: {'US', 'FR', 'AQ'},
  -143: {'US', 'FR', 'AQ'},
  -142: {'US', 'FR', 'AQ'},
  -141: {'US', 'FR', 'CA', 'AQ'},
  -140: {'FR', 'CA', 'AQ'},
  -139: {'FR', 'CA', 'AQ'},
  -138: {'US', 'FR', 'CA', 'AQ'},
  -137: {'US', 'FR', 'CA', 'AQ'},
  -136: {'US', 'FR', 'CA', 'AQ'},
  -135: {'US', 'FR', 'CA', 'AQ'},
  -134: {'US', 'CA', 'AQ'},
  -133: {'US', 'CA', 'AQ'},
  -132: {'US', 'CA', 'AQ'},
  -131: {'US', 'CA', 'AQ'},
  -130: {'CA', 'AQ'},
  -129: {'CA', 'AQ'},
  -128: {'CA', 'AQ'},
  -127: {'CA', 'AQ'},
  -126: {'CA', 'AQ'},
  -125: {'US', 'CA', 'AQ'},
  -124: {'US', 'CA', 'AQ'},
  -123: {'US', 'CA', 'AQ'},
  -122: {'US', 'CA', 'AQ'},
  -121: {'US', 'CA', 'AQ'},
  -120: {'US', 'CA', 'AQ'},
  -119: {'US', 'CA', 'AQ'},
  -118: {'US', 'CA', 'AQ', 'MX'},
  -117: {'US', 'CA', 'AQ', 'MX'},
  -116: {'US', 'CA', 'AQ', 'MX'},
  -115: {'US', 'CA', 'AQ', 'MX'},
  -114: {'US', 'CA', 'AQ', 'MX'},
  -113: {'US', 'CA', 'AQ', 'MX'},
  -112: {'US', 'CA', 'AQ', 'MX'},
  -111: {'US', 'CA', 'AQ', 'MX'},
  -110: {'US', 'CA', 'AQ', 'MX'},
  -109: {'US', 'CA', 'AQ', 'MX'},
  -108: {'US', 'CA', 'AQ', 'MX'},
  -107: {'US', 'CA', 'AQ', 'MX'},
  -106: {'US', 'CA', 'AQ', 'MX'},
  -105: {'US', 'CA', 'AQ', 'MX'},
  -104: {'US', 'CA', 'AQ', 'MX'},
  -103: {'US', 'CA', 'AQ', 'MX'},
  -102: {'US', 'CA', 'AQ', 'MX'},
  -101: {'US', 'CA', 'AQ', 'MX'},
  -100: {'US', 'CA', 'AQ', 'MX'},
  -99: {'US', 'CA', 'AQ', 'MX'},
  -98: {'US', 'CA', 'AQ', 'MX'},
  -97: {'US', 'CA', 'AQ', 'MX'},
  -96: {'US', 'CA', 'AQ', 'MX'},
  -95: {'US', 'CA', 'AQ', 'MX'},
  -94: {'US', 'CA', 'AQ', 'MX'},
  -93: {'CA', 'EC', 'GT', 'AQ', 'US', 'MX'},
  -92: {'CA', 'EC', 'GT', 'AQ', 'US', 'MX'},
  -91: {'CA', 'EC', 'GT', 'AQ', 'US', 'MX'},
  -90: {'BZ', 'CA', 'HN', 'EC', 'GT', 'SV', 'AQ', 'US', 'MX'},
  -89: {'BZ', 'CA', 'HN', 'AQ', 'SV', 'US', 'MX'},
  -88: {'BZ', 'CA', 'HN', 'NI', 'AQ', 'US', 'MX'},
  -87: {'US', 'AQ', 'CA', 'NI', 'HN'},
  -86: {'CR', 'CA', 'NI', 'HN', 'CU', 'AQ', 'US'},
  -85: {'CR', 'CA', 'NI', 'HN', 'PE', 'AQ', 'CU', 'US'},
  -84: {'CR', 'CA', 'NI', 'HN', 'PE', 'AQ', 'CU', 'US'},
  -83: {'PA', 'CR', 'CA', 'PE', 'CU', 'AQ', 'US'},
  -82: {'PA', 'CO', 'CA', 'PE', 'EC', 'AQ', 'CU', 'US'},
  -81: {'PA', 'CO', 'BS', 'CA', 'PE', 'EC', 'AQ', 'CU', 'US'},
  -80: {'PA', 'CO', 'BS', 'CA', 'PE', 'EC', 'AQ', 'CU', 'US'},
  -79: {'JM', 'PA', 'CO', 'BS', 'CA', 'PE', 'EC', 'AQ', 'CU', 'US'},
  -78: {'JM', 'PA', 'CO', 'BS', 'CA', 'PE', 'EC', 'AQ', 'CU', 'US'},
  -77: {'JM', 'CO', 'BS', 'CA', 'PE', 'CL', 'EC', 'AQ', 'CU', 'US'},
  -76: {'JM', 'CO', 'BS', 'CA', 'PE', 'CL', 'EC', 'AQ', 'CU', 'US'},
  -75: {'CO', 'BS', 'CA', 'PE', 'CL', 'AQ', 'CU', 'US', 'HT'},
  -74: {'GL', 'CO', 'AR', 'BS', 'CA', 'CL', 'PE', 'AQ', 'US', 'HT'},
  -73: {'US', 'GL', 'CO', 'VE', 'AR', 'BS', 'CA', 'CL', 'DO', 'PE', 'AQ', 'BR', 'HT', 'TC'},
  -72: {'US', 'GL', 'CO', 'VE', 'AR', 'CA', 'CL', 'DO', 'PE', 'AQ', 'BR', 'HT', 'TC'},
  -71: {'US', 'GL', 'CO', 'VE', 'AR', 'CA', 'CL', 'DO', 'PE', 'AQ', 'BR'},
  -70: {'US', 'GL', 'CO', 'VE', 'AR', 'CA', 'CL', 'DO', 'PE', 'AQ', 'BR', 'NL', 'BO'},
  -69: {'US', 'GL', 'CO', 'VE', 'AR', 'CA', 'CL', 'DO', 'PE', 'AQ', 'BR', 'NL', 'BO'},
  -68: {'US', 'GL', 'CO', 'VE', 'AR', 'CA', 'CL', 'AQ', 'BR', 'BO'},
  -67: {'US', 'GL', 'VE', 'AR', 'CA', 'CL', 'PR', 'AQ', 'BR', 'BO'},
  -66: {'GL', 'VE', 'AR', 'CA', 'PR', 'AQ', 'BR', 'BO'},
  -65: {'GL', 'VE', 'AR', 'CA', 'AQ', 'BR', 'VG', 'BO'},
  -64: {'GL', 'VE', 'AR', 'CA', 'AQ', 'BR', 'NL', 'BO'},
  -63: {'BO', 'GL', 'KN', 'VE', 'AR', 'CA', 'GD', 'AQ', 'PY', 'BR', 'NL', 'AG'},
  -62: {'FK', 'GL', 'GY', 'VC', 'TT', 'VE', 'CA', 'AR', 'LC', 'GD', 'AQ', 'PY', 'BR', 'FR', 'AG', 'BO', 'DM'},
  -61: {'FK', 'GL', 'GY', 'VC', 'TT', 'VE', 'CA', 'AR', 'LC', 'BB', 'AQ', 'PY', 'BR', 'FR', 'BO', 'DM'},
  -60: {'FK', 'GL', 'GY', 'VE', 'AR', 'CA', 'BB', 'AQ', 'PY', 'BR', 'BO'},
  -59: {'FK', 'GY', 'GL', 'SR', 'AR', 'CA', 'PY', 'AQ', 'BR', 'BO', 'UY'},
  -58: {'FK', 'GY', 'GL', 'SR', 'AR', 'CA', 'PY', 'AQ', 'BR', 'BO', 'UY'},
  -57: {'GY', 'GL', 'SR', 'AR', 'CA', 'PY', 'AQ', 'BR', 'UY'},
  -56: {'GL', 'SR', 'AR', 'CA', 'AQ', 'PY', 'BR', 'UY'},
  -55: {'GL', 'SR', 'AR', 'CA', 'AQ', 'PY', 'BR', 'FR', 'UY'},
  -54: {'GL', 'SR', 'AR', 'CA', 'AQ', 'BR', 'FR', 'UY'},
  -53: {'BR', 'FR', 'AQ', 'GL'},
  -52: {'BR', 'FR', 'AQ', 'GL'},
  -51: {'BR', 'AQ', 'GL'},
  -50: {'BR', 'AQ', 'GL'},
  -49: {'BR', 'AQ', 'GL'},
  -48: {'BR', 'AQ', 'GL'},
  -47: {'BR', 'AQ', 'GL'},
  -46: {'BR', 'AQ', 'GL'},
  -45: {'BR', 'AQ', 'GL'},
  -44: {'BR', 'AQ', 'GL'},
  -43: {'BR', 'AQ', 'GL'},
  -42: {'BR', 'AQ', 'GL'},
  -41: {'BR', 'AQ', 'GL'},
  -40: {'BR', 'AQ', 'GL'},
  -39: {'BR', 'AQ', 'GL', 'GS'},
  -38: {'BR', 'AQ', 'GL', 'GS'},
  -37: {'BR', 'AQ', 'GL', 'GS'},
  -36: {'BR', 'AQ', 'GL', 'GS'},
  -35: {'AQ', 'GL'},
  -34: {'AQ', 'GL'},
  -33: {'AQ', 'GL'},
  -32: {'AQ', 'GL'},
  -31: {'AQ', 'GL'},
  -30: {'AQ', 'GL'},
  -29: {'PT', 'AQ', 'GL'},
  -28: {'PT', 'GS', 'AQ', 'GL'},
  -27: {'PT', 'GS', 'AQ', 'GL'},
  -26: {'PT', 'CV', 'AQ', 'GL'},
  -25: {'PT', 'CV', 'IS', 'GL', 'AQ'},
  -24: {'CV', 'IS', 'GL', 'AQ'},
  -23: {'CV', 'IS', 'GL', 'AQ'},
  -22: {'IS', 'GL', 'AQ'},
  -21: {'IS', 'GL', 'AQ'},
  -20: {'IS', 'GL', 'AQ'},
  -19: {'IS', 'ES', 'GL', 'AQ'},
  -18: {'ES', 'GL', 'MR', 'PT', 'SN', 'MA', 'AQ', 'IS'},
  -17: {'GW', 'ES', 'GL', 'GM', 'PT', 'MR', 'SN', 'MA', 'AQ', 'IS'},
  -16: {'GW', 'ES', 'GL', 'GM', 'PT', 'MR', 'SN', 'MA', 'AQ', 'IS'},
  -15: {'GW', 'ES', 'GL', 'GM', 'MR', 'SN', 'EH', 'MA', 'AQ', 'GN', 'IS'},
  -14: {'GW', 'ES', 'GL', 'GM', 'SL', 'MR', 'SN', 'EH', 'MA', 'AQ', 'GN', 'IS'},
  -13: {'MR', 'GL', 'SL', 'ML', 'SN', 'EH', 'MA', 'AQ', 'GN'},
  -12: {'MR', 'GL', 'SL', 'ML', 'SN', 'IE', 'EH', 'MA', 'AQ', 'GN', 'LR'},
  -11: {'MR', 'SL', 'ML', 'IE', 'EH', 'MA', 'AQ', 'GN', 'LR'},
  -10: {'ES', 'MR', 'PT', 'ML', 'NO', 'IE', 'EH', 'MA', 'AQ', 'GN', 'LR'},
  -9: {'DZ', 'ES', 'MR', 'PT', 'NO', 'ML', 'CI', 'IE', 'EH', 'MA', 'AQ', 'GN', 'LR'},
  -8: {'DZ', 'ES', 'MR', 'NO', 'ML', 'PT', 'CI', 'GB', 'IE', 'MA', 'AQ', 'GN', 'FO', 'LR'},
  -7: {'DZ', 'ES', 'MR', 'ML', 'PT', 'CI', 'GB', 'IE', 'MA', 'AQ', 'FO'},
  -6: {'DZ', 'ES', 'MR', 'ML', 'GB', 'CI', 'IE', 'MA', 'AQ', 'GI', 'BF', 'IM'},
  -5: {'DZ', 'ES', 'ML', 'GB', 'CI', 'MA', 'AQ', 'GI', 'BF', 'IM', 'FR'},
  -4: {'DZ', 'ES', 'ML', 'GB', 'CI', 'MA', 'AQ', 'GH', 'BF', 'FR'},
  -3: {'DZ', 'ES', 'ML', 'JE', 'CI', 'GB', 'MA', 'AQ', 'GH', 'FR'},
  -2: {'DZ', 'ES', 'ML', 'JE', 'GB', 'MA', 'AQ', 'GH', 'FR'},
  -1: {'DZ', 'ES', 'ML', 'GB', 'AQ', 'GH', 'BF', 'FR'},
  0: {'DZ', 'ES', 'ML', 'BJ', 'TG', 'GB', 'AQ', 'NE', 'GH', 'BF', 'FR'},
  1: {'DZ', 'AD', 'ES', 'ML', 'BJ', 'TG', 'GB', 'AQ', 'NE', 'GH', 'BF', 'FR'},
  2: {'BE', 'DZ', 'AD', 'ES', 'NG', 'ML', 'BJ', 'AQ', 'NE', 'BF', 'FR'},
  3: {'BE', 'DZ', 'ES', 'NG', 'ML', 'BJ', 'AQ', 'NE', 'FR', 'NL'},
  4: {'BE', 'DZ', 'ES', 'NG', 'NO', 'ML', 'AQ', 'NE', 'FR', 'NL'},
  5: {'BE', 'DZ', 'LU', 'NG', 'NO', 'DE', 'AQ', 'NE', 'FR', 'NL'},
  6: {'ST', 'DZ', 'LU', 'IT', 'NG', 'NO', 'DE', 'CH', 'AQ', 'NE', 'FR', 'NL'},
  7: {'ST', 'DZ', 'IT', 'TN', 'NO', 'NG', 'MC', 'DE', 'CH', 'AQ', 'NE', 'FR', 'NL', 'DK'},
  8: {'DZ', 'GA', 'IT', 'TN', 'NO', 'CM', 'NG', 'DE', 'CH', 'AQ', 'NE', 'FR', 'DK'},
  9: {'SJ', 'DZ', 'LI', 'GA', 'IT', 'TN', 'NO', 'CM', 'NG', 'DE', 'CH', 'LY', 'AQ', 'NE', 'GQ', 'AT', 'FR', 'DK'},
  10: {'SJ', 'DZ', 'GA', 'IT', 'TN', 'NO', 'CM', 'NG', 'DE', 'LY', 'GQ', 'AQ', 'NE', 'AT', 'SE', 'DK'},
  11: {'SJ', 'DZ', 'GA', 'IT', 'AO', 'TN', 'NO', 'CM', 'NG', 'VA', 'NA', 'DE', 'CG', 'LY', 'GQ', 'AQ', 'NE', 'AT', 'SE', 'DK'},
  12: {'SJ', 'GA', 'AO', 'IT', 'NG', 'CD', 'CM', 'NO', 'VA', 'NA', 'DE', 'CG', 'SM', 'LY', 'AQ', 'NE', 'CZ', 'AT', 'SE', 'DK'},
  13: {'SJ', 'GA', 'AT', 'AO', 'IT', 'NG', 'CD', 'CM', 'NO', 'DE', 'NA', 'CG', 'HR', 'LY', 'AQ', 'NE', 'CZ', 'SI', 'TD', 'SE', 'MT', 'DK'},
  14: {'SJ', 'GA', 'AO', 'CG', 'HR', 'LY', 'NE', 'IT', 'CD', 'CM', 'AQ', 'CZ', 'SE', 'NO', 'MT', 'DK', 'NG', 'PL', 'CF', 'DE', 'NA', 'SI', 'TD', 'AT'},
  15: {'SJ', 'AT', 'IT', 'AO', 'CD', 'CM', 'NO', 'PL', 'NA', 'CF', 'CG', 'LY', 'HR', 'AQ', 'NE', 'BA', 'SI', 'CZ', 'SE', 'TD', 'DK'},
  16: {'SJ', 'HU', 'IT', 'AO', 'CD', 'ZA', 'PL', 'NO', 'CM', 'NA', 'CF', 'CG', 'HR', 'LY', 'AQ', 'BA', 'CZ', 'AT', 'TD', 'SE'},
  17: {'SJ', 'HU', 'IT', 'AO', 'CD', 'ZA', 'PL', 'NO', 'NA', 'CF', 'CG', 'HR', 'LY', 'AQ', 'BA', 'SK', 'AT', 'CZ', 'TD', 'SE'},
  18: {'SJ', 'HU', 'IT', 'AO', 'CD', 'ZA', 'PL', 'NO', 'NA', 'CF', 'CG', 'HR', 'LY', 'AQ', 'BA', 'SK', 'TD', 'CZ', 'SE', 'ME'},
  19: {'SJ', 'HU', 'AL', 'RS', 'AO', 'BW', 'CD', 'ZA', 'NO', 'PL', 'FI', 'CF', 'NA', 'HR', 'LY', 'AQ', 'BA', 'SK', 'TD', 'SE', 'ME'},
  20: {'SJ', 'HU', 'AL', 'RO', 'AO', 'BW', 'LV', 'FI', 'MK', 'LY', 'SK', 'XK', 'RS', 'CD', 'ZA', 'AQ', 'LT', 'SE', 'ME', 'NO', 'GR', 'PL', 'CF', 'NA', 'TD'},
  21: {'SJ', 'HU', 'RO', 'SD', 'AO', 'BW', 'LV', 'FI', 'MK', 'LY', 'SK', 'XK', 'EE', 'RS', 'CD', 'ZA', 'AQ', 'LT', 'SE', 'NO', 'GR', 'PL', 'CF', 'NA', 'TD'},
  22: {'SJ', 'HU', 'RO', 'SD', 'AO', 'BW', 'LV', 'FI', 'MK', 'LY', 'SK', 'EE', 'UA', 'RS', 'CD', 'ZA', 'AQ', 'LT', 'SE', 'BG', 'ZM', 'NO', 'GR', 'PL', 'CF', 'NA', 'TD'},
  23: {'SJ', 'RO', 'SD', 'AO', 'BW', 'LV', 'FI', 'LY', 'EE', 'UA', 'CD', 'ZA', 'AQ', 'LT', 'SE', 'BG', 'ZM', 'NO', 'GR', 'PL', 'CF', 'NA', 'TD', 'BY'},
  24: {'SJ', 'RO', 'SD', 'AO', 'BW', 'LV', 'FI', 'LY', 'EE', 'UA', 'CD', 'ZA', 'AQ', 'LT', 'SE', 'BG', 'ZM', 'SS', 'NO', 'EG', 'GR', 'CF', 'NA', 'BY'},
  25: {'SJ', 'RO', 'SD', 'BW', 'LV', 'FI', 'LY', 'EE', 'UA', 'CD', 'ZA', 'ZW', 'AQ', 'LT', 'BG', 'ZM', 'SS', 'NO', 'EG', 'GR', 'CF', 'TR', 'BY'},
  26: {'SJ', 'ZM', 'RO', 'UA', 'GR', 'SD', 'BW', 'SS', 'CD', 'ZA', 'NO', 'LV', 'ZW', 'FI', 'CF', 'EG', 'TR', 'AQ', 'LT', 'BG', 'EE', 'BY'},
  27: {'SJ', 'RO', 'SD', 'BW', 'LV', 'FI', 'EE', 'UA', 'LS', 'CD', 'ZA', 'ZW', 'MD', 'AQ', 'BG', 'ZM', 'SS', 'NO', 'EG', 'GR', 'TR', 'BY'},
  28: {'SJ', 'ZM', 'RO', 'UA', 'LS', 'GR', 'SD', 'BW', 'SS', 'CD', 'ZA', 'NO', 'RU', 'ZW', 'FI', 'EG', 'MD', 'TR', 'AQ', 'BG', 'BY'},
  29: {'SJ', 'RO', 'SD', 'BW', 'BI', 'FI', 'UG', 'TZ', 'UA', 'LS', 'CD', 'ZA', 'ZW', 'MD', 'AQ', 'ZM', 'SS', 'NO', 'RU', 'EG', 'TR', 'RW', 'BY'},
  30: {'SJ', 'ZM', 'RO', 'UA', 'MZ', 'SS', 'SD', 'CD', 'ZA', 'NO', 'RU', 'BI', 'FI', 'ZW', 'EG', 'UG', 'TR', 'AQ', 'RW', 'SZ', 'TZ', 'BY'},
  31: {'SJ', 'ZM', 'UA', 'MZ', 'SS', 'SD', 'CD', 'ZA', 'NO', 'RU', 'ZW', 'FI', 'EG', 'UG', 'TR', 'AQ', 'SZ', 'TZ', 'BY'},
  32: {'SJ', 'ZM', 'UA', 'MZ', 'SS', 'SD', 'NO', 'ZA', 'RU', 'ZW', 'CY', 'EG', 'UG', 'TR', 'AQ', 'MW', 'SZ', 'TZ'},
  33: {'SJ', 'ZM', 'ET', 'UA', 'MZ', 'SD', 'SS', 'NO', 'ZA', 'RU', 'ZW', 'CY', 'EG', 'UG', 'TR', 'AQ', 'KE', 'MW', 'TZ'},
  34: {'SJ', 'ET', 'PS', 'UA', 'MZ', 'SD', 'SS', 'NO', 'RU', 'SA', 'CY', 'IL', 'EG', 'UG', 'TR', 'AQ', 'KE', 'MW', 'TZ'},
  35: {'ET', 'PS', 'UA', 'MZ', 'SD', 'SS', 'SY', 'JO', 'RU', 'SA', 'IL', 'EG', 'UG', 'TR', 'AQ', 'KE', 'MW', 'LB', 'TZ'},
  36: {'ET', 'UA', 'MZ', 'SD', 'SY', 'JO', 'RU', 'SA', 'EG', 'TR', 'AQ', 'KE', 'LB', 'ER', 'TZ'},
  37: {'ET', 'UA', 'MZ', 'SD', 'SY', 'JO', 'ZA', 'RU', 'SA', 'TR', 'AQ', 'KE', 'ER', 'TZ'},
  38: {'ET', 'UA', 'MZ', 'SD', 'SY', 'JO', 'ZA', 'RU', 'SA', 'TR', 'AQ', 'KE', 'IQ', 'ER', 'TZ'},
  39: {'ET', 'UA', 'MZ', 'SY', 'JO', 'RU', 'SA', 'TR', 'AQ', 'KE', 'IQ', 'ER', 'TZ'},
  40: {'ET', 'MZ', 'SY', 'RU', 'ER', 'SO', 'SA', 'TR', 'AQ', 'KE', 'IQ', 'GE', 'TZ'},
  41: {'ET', 'DJ', 'MZ', 'SY', 'RU', 'ER', 'SO', 'SA', 'YE', 'AQ', 'KE', 'IQ', 'TR', 'GE'},
  42: {'ET', 'MG', 'DJ', 'SY', 'RU', 'ER', 'SO', 'SA', 'YE', 'AQ', 'TR', 'IQ', 'GE'},
  43: {'ET', 'MG', 'DJ', 'RU', 'ER', 'SO', 'SA', 'KM', 'AM', 'YE', 'AQ', 'TR', 'IQ', 'GE'},
  44: {'ET', 'IR', 'MG', 'RU', 'SO', 'SA', 'KM', 'AM', 'YE', 'AQ', 'TR', 'IQ', 'GE', 'FR'},
  45: {'ET', 'IR', 'MG', 'AZ', 'RU', 'SO', 'SA', 'AM', 'YE', 'AQ', 'IQ', 'GE', 'FR'},
  46: {'ET', 'IR', 'MG', 'KZ', 'RU', 'AZ', 'SO', 'SA', 'YE', 'AQ', 'IQ', 'GE'},
  47: {'TF', 'IR', 'MG', 'KZ', 'RU', 'AZ', 'SO', 'SA', 'YE', 'AQ', 'IQ', 'QA', 'KW'},
  48: {'TF', 'IR', 'MG', 'KZ', 'RU', 'AZ', 'SO', 'SA', 'YE', 'AQ', 'QA', 'KW'},
  49: {'TF', 'IR', 'MG', 'KZ', 'RU', 'AZ', 'SO', 'SA', 'YE', 'AQ', 'QA', 'FR'},
  50: {'TF', 'IR', 'MG', 'KZ', 'RU', 'SO', 'SA', 'SC', 'YE', 'AQ', 'QA', 'FR'},
  51: {'IR', 'TF', 'KZ', 'RU', 'SO', 'SA', 'SC', 'OM', 'AE', 'YE', 'AQ', 'QA'},
  52: {'IR', 'TF', 'KZ', 'RU', 'SA', 'SC', 'OM', 'AE', 'YE', 'AQ', 'TM'},
  53: {'IR', 'TF', 'KZ', 'RU', 'SA', 'SC', 'OM', 'AE', 'YE', 'AQ', 'TM'},
  54: {'IR', 'TF', 'KZ', 'RU', 'SA', 'OM', 'AE', 'AQ', 'QA', 'TM'},
  55: {'IR', 'TF', 'KZ', 'RU', 'RE', 'SA', 'OM', 'AE', 'UZ', 'AQ', 'QA', 'TM'},
  56: {'IR', 'TF', 'KZ', 'RU', 'OM', 'AE', 'UZ', 'AQ', 'TM'},
  57: {'IR', 'TF', 'KZ', 'RU', 'OM', 'UZ', 'AQ', 'MU', 'TM'},
  58: {'IR', 'TF', 'KZ', 'RU', 'OM', 'UZ', 'AQ', 'TM'},
  59: {'IR', 'TF', 'KZ', 'RU', 'OM', 'UZ', 'AQ', 'TM'},
  60: {'IR', 'TF', 'AF', 'KZ', 'RU', 'UZ', 'AQ', 'TM'},
  61: {'IR', 'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  62: {'IR', 'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  63: {'IR', 'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  64: {'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  65: {'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  66: {'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TM'},
  67: {'TF', 'AF', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TJ', 'FR'},
  68: {'TF', 'AF', 'IN', 'KZ', 'RU', 'UZ', 'PK', 'AQ', 'TJ', 'FR'},
  69: {'TF', 'AF', 'IN', 'KZ', 'RU', 'KG', 'UZ', 'PK', 'AQ', 'TJ', 'FR'},
  70: {'TF', 'AF', 'IN', 'KZ', 'RU', 'KG', 'UZ', 'PK', 'AQ', 'TJ', 'FR'},
  71: {'TF', 'AF', 'IN', 'KZ', 'RU', 'KG', 'UZ', 'PK', 'AQ', 'TJ'},
  72: {'TF', 'AF', 'MV', 'KZ', 'IN', 'KG', 'RU', 'UZ', 'PK', 'AQ', 'TJ'},
  73: {'AU', 'TF', 'AF', 'MV', 'KZ', 'IN', 'KG', 'RU', 'PK', 'AQ', 'TJ'},
  74: {'CN', 'TF', 'AF', 'IN', 'KZ', 'RU', 'KG', 'TJ', 'PK', 'AQ'},
  75: {'CN', 'TF', 'IN', 'KZ', 'RU', 'KG', 'PK', 'AQ'},
  76: {'CN', 'IN', 'KZ', 'RU', 'KG', 'PK', 'AQ'},
  77: {'CN', 'IN', 'KZ', 'RU', 'KG', 'AQ'},
  78: {'CN', 'IN', 'KZ', 'RU', 'KG', 'AQ'},
  79: {'CN', 'IN', 'KZ', 'LK', 'RU', 'KG', 'AQ'},
  80: {'CN', 'IN', 'KZ', 'LK', 'RU', 'AQ', 'NP'},
  81: {'CN', 'IN', 'KZ', 'LK', 'RU', 'AQ', 'NP'},
  82: {'CN', 'IN', 'KZ', 'LK', 'RU', 'AQ', 'NP'},
  83: {'CN', 'IN', 'KZ', 'RU', 'AQ', 'NP'},
  84: {'CN', 'IN', 'KZ', 'RU', 'AQ', 'NP'},
  85: {'CN', 'IN', 'KZ', 'RU', 'AQ', 'NP'},
  86: {'CN', 'IN', 'KZ', 'RU', 'AQ', 'NP'},
  87: {'CN', 'IN', 'RU', 'AQ', 'NP', 'MN'},
  88: {'CN', 'BD', 'IN', 'RU', 'BT', 'AQ', 'NP', 'MN'},
  89: {'CN', 'BD', 'IN', 'RU', 'BT', 'AQ', 'MN'},
  90: {'CN', 'BD', 'IN', 'RU', 'BT', 'AQ', 'MN'},
  91: {'CN', 'BD', 'IN', 'RU', 'BT', 'AQ', 'MN'},
  92: {'CN', 'BD', 'IN', 'RU', 'MM', 'BT', 'AQ', 'MN'},
  93: {'CN', 'IN', 'RU', 'MM', 'AQ', 'MN'},
  94: {'CN', 'IN', 'RU', 'MM', 'AQ', 'MN', 'ID'},
  95: {'CN', 'IN', 'RU', 'MM', 'AQ', 'MN', 'ID'},
  96: {'CN', 'IN', 'RU', 'MM', 'AQ', 'MN', 'ID'},
  97: {'CN', 'IN', 'RU', 'MM', 'AQ', 'MN', 'ID', 'TH'},
  98: {'CN', 'RU', 'MM', 'AQ', 'MN', 'ID', 'TH'},
  99: {'CN', 'RU', 'MM', 'AQ', 'MN', 'ID', 'TH', 'MY'},
  100: {'CN', 'RU', 'MM', 'LA', 'AQ', 'MN', 'ID', 'TH', 'MY'},
  101: {'CN', 'RU', 'LA', 'AQ', 'MN', 'ID', 'TH', 'MY'},
  102: {'CN', 'ID', 'RU', 'LA', 'AQ', 'MN', 'VN', 'TH', 'KH', 'MY'},
  103: {'CN', 'ID', 'RU', 'SG', 'LA', 'AQ', 'MN', 'VN', 'TH', 'KH', 'MY'},
  104: {'CN', 'ID', 'RU', 'LA', 'AQ', 'MN', 'VN', 'TH', 'KH', 'MY'},
  105: {'CN', 'ID', 'RU', 'LA', 'AQ', 'MN', 'VN', 'TH', 'KH'},
  106: {'CN', 'ID', 'RU', 'LA', 'AQ', 'MN', 'VN', 'KH'},
  107: {'CN', 'ID', 'RU', 'LA', 'AQ', 'MN', 'VN', 'KH'},
  108: {'CN', 'ID', 'RU', 'AQ', 'MN', 'VN'},
  109: {'CN', 'ID', 'RU', 'AQ', 'MN', 'VN', 'MY'},
  110: {'CN', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  111: {'CN', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  112: {'CN', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  113: {'AU', 'CN', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  114: {'AU', 'CN', 'RU', 'BN', 'AQ', 'MN', 'ID', 'MY'},
  115: {'AU', 'CN', 'RU', 'BN', 'AQ', 'MN', 'ID', 'MY'},
  116: {'AU', 'CN', 'PH', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  117: {'AU', 'CN', 'PH', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  118: {'AU', 'CN', 'PH', 'RU', 'AQ', 'MN', 'ID', 'MY'},
  119: {'AU', 'CN', 'PH', 'RU', 'TW', 'AQ', 'MN', 'ID', 'MY'},
  120: {'AU', 'CN', 'PH', 'RU', 'TW', 'AQ', 'ID'},
  121: {'AU', 'CN', 'PH', 'RU', 'TW', 'AQ', 'ID'},
  122: {'AU', 'CN', 'PH', 'RU', 'TW', 'AQ', 'ID'},
  123: {'AU', 'CN', 'PH', 'JP', 'RU', 'AQ', 'ID'},
  124: {'KR', 'AU', 'CN', 'KP', 'PH', 'JP', 'RU', 'AQ', 'ID', 'TL'},
  125: {'KR', 'AU', 'CN', 'KP', 'PH', 'JP', 'RU', 'AQ', 'ID', 'TL'},
  126: {'KR', 'AU', 'CN', 'KP', 'PH', 'JP', 'RU', 'AQ', 'ID', 'TL'},
  127: {'KR', 'AU', 'CN', 'KP', 'JP', 'RU', 'AQ', 'ID'},
  128: {'KR', 'AU', 'CN', 'KP', 'JP', 'RU', 'AQ', 'ID'},
  129: {'KR', 'AU', 'CN', 'KP', 'JP', 'RU', 'AQ', 'ID'},
  130: {'KP', 'AU', 'CN', 'JP', 'RU', 'AQ', 'ID'},
  131: {'AU', 'CN', 'JP', 'RU', 'AQ', 'ID'},
  132: {'AU', 'CN', 'JP', 'RU', 'AQ', 'ID'},
  133: {'AU', 'CN', 'JP', 'RU', 'AQ', 'ID'},
  134: {'AU', 'ID', 'RU', 'AQ', 'JP'},
  135: {'AU', 'ID', 'RU', 'AQ', 'JP'},
  136: {'AU', 'ID', 'RU', 'AQ', 'JP'},
  137: {'AU', 'ID', 'RU', 'AQ', 'JP'},
  138: {'AU', 'ID', 'RU', 'AQ', 'JP'},
  139: {'AU', 'JP', 'RU', 'AQ', 'ID', 'FM'},
  140: {'AU', 'JP', 'RU', 'AQ', 'ID', 'FM'},
  141: {'AU', 'JP', 'RU', 'AQ', 'ID', 'PG'},
  142: {'AU', 'RU', 'PG', 'AQ', 'JP'},
  143: {'AU', 'RU', 'PG', 'AQ', 'JP'},
  144: {'AU', 'RU', 'PG', 'AQ', 'JP'},
  145: {'AU', 'JP', 'RU', 'AQ', 'US', 'PG'},
  146: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  147: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  148: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  149: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  150: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  151: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  152: {'AU', 'RU', 'FM', 'PG', 'AQ'},
  153: {'RU', 'FM', 'PG', 'AQ'},
  154: {'RU', 'FM', 'PG', 'AQ'},
  155: {'RU', 'FM', 'PG', 'AQ', 'SB'},
  156: {'RU', 'FM', 'AQ', 'SB'},
  157: {'RU', 'FM', 'AQ', 'SB'},
  158: {'RU', 'FR', 'FM', 'AQ', 'SB'},
  159: {'RU', 'FR', 'AQ', 'SB'},
  160: {'RU', 'MH', 'AQ', 'SB'},
  161: {'RU', 'MH', 'AQ', 'SB'},
  162: {'NC', 'RU', 'MH', 'SB', 'AQ', 'FR'},
  163: {'RU', 'MH', 'FR', 'NC', 'AQ'},
  164: {'RU', 'MH', 'FR', 'NC', 'AQ'},
  165: {'NC', 'RU', 'NZ', 'MH', 'SB', 'AQ', 'FR'},
  166: {'VU', 'NC', 'RU', 'NZ', 'MH', 'SB', 'AQ', 'FR'},
  167: {'VU', 'NC', 'RU', 'NZ', 'MH', 'SB', 'AQ', 'FR'},
  168: {'VU', 'NC', 'RU', 'NZ', 'MH', 'AQ', 'FR'},
  169: {'VU', 'NC', 'RU', 'NZ', 'MH', 'AQ'},
  170: {'RU', 'VU', 'MH', 'AQ', 'NZ'},
  171: {'RU', 'MH', 'AQ', 'NZ'},
  172: {'RU', 'KI', 'MH', 'AQ', 'NZ'},
  173: {'RU', 'KI', 'AQ', 'NZ'},
  174: {'RU', 'AQ', 'NZ'},
  175: {'RU', 'AQ', 'NZ'},
  176: {'RU', 'AQ', 'FJ', 'NZ'},
  177: {'RU', 'US', 'AQ', 'FJ', 'NZ'},
  178: {'RU', 'AQ', 'FJ', 'NZ'},
  179: {'RU', 'AQ', 'FJ'}
}
