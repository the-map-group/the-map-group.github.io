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

def getInfoFromDictionary(latlong, dictionary):
    country_info = ['', '']
    key = "{},{}".format(latlong[0], latlong[1])
    try:
        country_info = dictionary[key]
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

def getCountryInfo(lat, long, matrix_dict, coords_dict):

    use_matrix = countries_config.use_matrix
    update_matrix = countries_config.update_matrix
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

    code = ''
    name = ''

    if lat_long in not_found_places_list and lat_long not in not_found_places_excludes:
        log_file.write("{} skipped: [{}, {}] is at not found list\n".format(latlong, latitude, longitude))
        log_file.close()
        htm_file.close()
        if gen_rep_file:
            rep_file.close()
        if gen_err_file:
            err_file.close()
        return [code, name, matrix_dict, coords_dict]
    elif lat_long in not_found_places_excludes:
            log_file.write("{} not skipped: [{}, {}] is at not found excludes\n".format(latlong, latitude, longitude))

    if use_matrix:
        # get info from matrix dictionary
        info = getInfoFromDictionary(lat_long, matrix_dict)
        code = info[0]
        name = info[1]
        if code != '':
            if gen_rep_file and rep_matrix:
                rep_file.write("Matrix: {} = [{}, {}] => '{}: {}'\n".format(latlong, latitude, longitude, code, name))
            latlong_key = "{},{}".format(latitude, longitude)
            if latlong_key not in small_countries_dict.keys():
                matrix_dict[latlong_key] = [code, name]

    if code == '':

        # get info from coordinates dictionary
        info = getInfoFromDictionary(latlong, coords_dict)
        code = info[0]
        name = info[1]

        try:
            if name != countries_dict[code][0]:
                name = countries_dict[code][0]
                key = "{},{}".format(latlong[0], latlong[1])
                coords_dict[key] = [code, name]
        except:
            pass

        if code != '':
            if gen_rep_file:
                if rep_dictionary:
                    rep_file.write("Coords Dictionary: {} = '{}: {}'\n".format(latlong, code, name))
                rep_file.close()
            if gen_err_file:
                err_file.close()
            log_file.close()
            htm_file.close()

            return [code, name, matrix_dict, coords_dict]

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

            if (code == '*' or code in geonames_exclude) and use_mapbox:
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
                    rep_file.write("--> \'{}: {}\' = \'{}\' ".format(code, name, countries_dict[code][0]))
                try:
                    code = codes_dict[name]
                except:
                    pass
                try:
                    name = countries_dict[code][0]
                    if gen_rep_file:
                        rep_file.write("=> \'{}: {}'\n".format(code, name))
                except:
                    if gen_rep_file:
                        rep_file.write("\n")
        except:
            if gen_rep_file and code != '' and code != '*':
                rep_file.write("--> \'{}: {}\' = NOT FOUND AT DICTIONARY\n".format(code, name))

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
                htm_file.write("{} Unable to find the name of the location<br>\n".format(latlong))
                log_file.write("{} Unable to find the name of the location\n".format(latlong))

        # assign correct code and name to some countries using the dictionaries
        try:
            if name != countries_dict[code][0]:
                if gen_rep_file:
                    rep_file.write("---> \'{}: {}\' = \'{}\' ".format(code, name, countries_dict[code][0]))
                try:
                    code = codes_dict[name]
                except:
                    pass
                try:
                    name = countries_dict[code][0]
                    if gen_rep_file:
                        rep_file.write("=> \'{}: {}'\n".format(code, name))
                except:
                    if gen_rep_file:
                        rep_file.write("\n")
        except:
            if code != '' and code != '*':
                rep_file.write("---> \'{}: {}\' = NOT FOUND AT DICTIONARY\n".format(code, name))

        # add coordinate to dictionary
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


        if update_matrix:

            exception_ocurred = False

            if code == '*' or code == '**':
                exception_ocurred = True
                code = ''
                name = ''

            if code != '':
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

                    code_01 = getInfoFromNominatim(coord_01)[0]
                    code_10 = getInfoFromNominatim(coord_10)[0]
                    code_11 = getInfoFromNominatim(coord_11)[0]

                    if code_01 == '':
                        code_01 = getInfoFromGeoNames(coord_01)[0]
                    if code_10 == '':
                        code_10 = getInfoFromGeoNames(coord_10)[0]
                    if code_11 == '':
                        code_11 = getInfoFromGeoNames(coord_11)[0]

                    if use_mapbox:
                        if code_01 == '':
                            code_01 = getInfoFromMapBox(coord_01)[0]
                        if code_10 == '':
                            code_10 = getInfoFromMapBox(coord_10)[0]
                        if code_11 == '':
                            code_11 = getInfoFromMapBox(coord_11)[0]

                    if (code_01 == code or code_01 == '') and (code_10 == code or code_10 == '') and (code_11 == code or code_11 == ''):
                        latlong_key = "{},{}".format(latitude, longitude)
                        if latlong_key not in small_countries_dict.keys():
                            matrix_dict[latlong_key] = [code, name]
                            if gen_rep_file:
                                rep_file.write("-->+ {} = '{}: {}' added to matrix dictionary\n".format(lat_long, code, name))
                        elif gen_rep_file:
                            small_country_code = small_countries_dict[latlong_key][0]
                            small_country_name = small_countries_dict[latlong_key][1]
                            rep_file.write("'{0}: {1}' is a small country inside square with origin in {2}\n--> {2} = '{3}: {4}' not added to matrix dictionary\n".format(small_country_code, small_country_name, lat_long, code, name))
                    else:
                        log_file.write("{} = '{}: {}' not added to matrix dictionary\n".format(lat_long, code, name))
                except:
                    pass

            if exception_ocurred:
                code = '*'
                name = ''

        htm_file.close()
        log_file.close()
        if gen_rep_file:
            rep_file.close()
        if gen_err_file:
            err_file.close()

    return [code, name, matrix_dict, coords_dict]


# dictionaries

countries_dict = {
    'AD': ['Andorra', [[1.405404, 42.427745, 1.795418, 42.656415]]],
    'AE': ['United Arab Emirates', [[51.5795186705, 22.4969475367, 56.3968473651, 26.055464179]]],
    'AF': ['Afghanistan', [[60.5284298033, 29.318572496, 75.1580277851, 38.4862816432]]],
    'AG': ['Antigua and Barbuda', [[-62.359054, 16.929362, -61.640823, 18.744734]]],
    'AI': ['Anguilla', [[-63.464673, 18.132158, -62.903737, 18.602913]]],
    'AL': ['Albania', [[18.3044861183, 39.624997667, 21.0200403175, 42.6882473822]]],
    'AM': ['Armenia', [[43.5827458026, 38.7412014837, 46.5057198423, 41.2481285671]]],
    'AO': ['Angola', [[11.6400960629, -17.9306364885, 24.0799052263, -4.43802336998]]],
    'AQ': ['Antarctica', [[-179.999, -90, 179.999, -58]]],
    'AR': ['Argentina', [[-73.4154357571, -55.25, -53.628348965, -21.8323104794]]],
    'AT': ['Austria', [[9.47996951665, 46.4318173285, 17.9796667823, 49.0390742051]]],
    'AU': ['Australia', [[111.338953078, -44.6345972634, 164.569469029, -9.6681857235]]],
    'AW': ['Aruba', [[-71.29452679952362, 12.407243342751821, -69.82504218458341, 14.639490542218121]]],
    'AZ': ['Azerbaijan', [[44.7939896991, 38.2703775091, 51.3928210793, 42.8606751572]]],
    'BA': ['Bosnia and Herzegovina', [[15.7500260759, 42.65, 19.59976, 45.2337767604]]],
    'BB': ['Barbados', [[-60.665815, 12.045699, -58.417162, 14.344526]]],
    'BD': ['Bangladesh', [[88.0844222351, 19.670883287, 92.6727209818, 26.4465255803]]],
    'BE': ['Belgium', [[2.51357303225, 49.5294835476, 6.35665815596, 51.4750237087]]],
    'BF': ['Burkina Faso', [[-5.47056494793, 9.61083486576, 2.17710778159, 15.1161577418]]],
    'BG': ['Bulgaria', [[22.3805257504, 41.2344859889, 29.5580814959, 44.2349230007]]],
    'BH': ['Bahrain', [[50.2470347746, 25.7659864082, 50.7709381768, 26.3683130773]]],
    'BI': ['Burundi', [[29.0249263852, -4.49998341229, 30.752262811, -2.34848683025]]],
    'BJ': ['Benin', [[0.772335646171, 5.14215770103, 3.79711225751, 12.2356358912]]],
    'BM': ['Bermuda', [[-66.893439, 31.244335, -63.642937, 33.393605]]],
    'BN': ['Brunei', [[114.204016555, 4.007636827, 115.450710484, 5.44772980389]]],
    'BO': ['Bolivia', [[-69.5904237535, -22.8729187965, -57.4983711412, -9.76198780685]]],
    'BQ': ['Bonaire', [[-69.432215, 11.021435, -63.161908, 18.355929]]],
    'BR': ['Brazil', [[-73.9872354804, -33.7683777809, -28.7299934555, 5.24448639569]]],
    'BS': ['Bahamas', [[-79.98, 20.51, -71.0, 27.24]]],
    'BT': ['Bhutan', [[88.8142484883, 26.7194029811, 92.1037117859, 28.2964385035]]],
    'BW': ['Botswana', [[19.8954577979, -26.8285429827, 29.4321883481, -17.6618156877]]],
    'BY': ['Belarus', [[23.1994938494, 51.3195034857, 32.6936430193, 56.1691299506]]],
    'BZ': ['Belize', [[-89.2291216703, 15.8869375676, -87.1068129138, 18.4999822047]]],
    'CA': ['Canada', [[-141.99778, 41.6751050889, -51.6480987209, 83.23324]]],
    'CD': ['Democratic Republic of the Congo', [[11.1823368669, -13.2572266578, 31.1741492042, 5.25608775474]]],
    'CF': ['Central African Republic', [[14.4594071794, 2.2676396753, 27.3742261085, 11.1423951278]]],
    'CG': ['Congo', [[11.0937728207, -5.03798674888, 18.4530652198, 3.72819651938]]],
    'CH': ['Switzerland', [[6.02260949059, 45.7769477403, 10.5427014502, 47.8308275417]]],
    'CI': ['Ivory Coast', [[-8.60288021487, 3.33828847902, -2.56218950033, 10.5240607772]]],
    'CK': ['Cook Islands', [[-166.951493, -22.024598, -156.156169, -8.819687]]],
    'CL': ['Chile', [[-79.6443953112, -56.61183, -65.95992, -17.5800118954], [-111.50362444697001, -28.230656820598767, -108.18057943196189, -26.03105539474612]]],
    'CM': ['Cameroon', [[8.48881554529, 1.72767263428, 16.0128524106, 12.8593962671]]],
    'CN': ['China', [[73.6753792663, 16.197700914, 135.026311477, 53.4588044297]]],
    'CO': ['Colombia', [[-80.9909352282, -4.29818694419, -66.8763258531, 14.6373031682], [-83.86911998323228, 11.365626736114, -80.2123476530185, 14.553411421411814]]],
    'CR': ['Costa Rica', [[-87.94172543, 7.22502798099, -82.5461962552, 11.2171192489]]],
    'CU': ['Cuba', [[-85.9749110583, 19.8554808619, -73.1480248685, 23.8886107447]]],
    'CV': ['Cape Verde', [[-27.455971, 14.706625, -21.497389, 17.224064]]],
    'CW': ['Curaçao', [[-69.21882845380156, 12.029359492620058, -68.65303257484364, 13.418583596006405]]],
    'CY': ['Cyprus', [[31.2566671079, 34.5718694118, 34.1048808123, 35.3931247015]]],
    'TY': ['Northern Cyprus', [[32.58167868811915, 34.964828049823055, 34.74720840589335, 35.7570382711454]]],
    'CZ': ['Czech Republic', [[12.2401111182, 48.5553052842, 18.8531441586, 51.1172677679]]],
    'DE': ['Germany', [[5.98865807458, 47.3024876979, 15.0169958839, 55.983104153]]],
    'DJ': ['Djibouti', [[41.66176, 10.9268785669, 43.3178524107, 12.6996385767]]],
    'DK': ['Denmark', [[6.08997684086, 54.6000145534, 16.6900061378, 58.930016588], [14.613165202397736, 54.96661755000927, 15.272102304381914, 55.322660495963795]]],
    'DM': ['Dominica', [[-61.470812, 15.208117, -61.235424, 15.647632]]],
    'DO': ['Dominican Republic', [[-71.9451120673, 17.598564358, -67.3179432848, 20.8849105901]]],
    'DZ': ['Algeria', [[-8.68439978681, 19.0573642034, 11.9995056495, 37.1183806422]]],
    'EC': ['Ecuador', [[-81.9677654691, -4.95912851321, -75.2337227037, 1.3809237736], [-91.78482012101239, -1.5824948711196969, -88.75636188841905, 0.9042588609438755]]],
    'EE': ['Estonia', [[20.3397953631, 57.4745283067, 28.2316992531, 59.6110903998]]],
    'EG': ['Egypt', [[24.70007, 21.0, 36.86623, 33.58568]]],
    'EH': ['Western Sahara', [[-17.443494, 20.589817, -8.538591, 27.733945]]],
    'ER': ['Eritrea', [[36.3231889178, 12.4554157577, 43.3812260272, 19.9983074]]],
    'ES': ['Spain', [[-10.39288367353, 35.926850084, 5.43948408368, 44.7483377142], [-19.569668805804973, 26.43668482526088, -12.972592777381738, 29.47483064876065], [-5.392763536146292, 35.86627481887327, -5.26521914459584, 35.92426331993819]]],
    'ET': ['Ethiopia', [[32.95418, 3.42206, 47.78942, 14.95943]]],
    'EU': ['European Union', [[-24.689924, 35.716942, 50.678160, 71.093955]]],
    'FI': ['Finland', [[19.6455928891, 59.746373196, 31.5160921567, 70.1641930203]]],
    'FJ': ['Fiji', [[-180.0, -22.28799, 180.0, -11.0208822567]]],
    'FK': ['Falkland Islands', [[-62.0, -53.3, -55.65, -50.9]]],
    'FM': ['Micronesia', [[136, 0, 164, 11]]],
    'FO': ['Faroe Islands', [[-9.723461, 60.381658, -4.215588, 63.396159]]],
    'FR': ['France', [[-7.616257, 42.417756, 9.56001631027, 51.3485061713], [7.425295708550317, 41.30316477790055, 10.614212396017411, 43.06493582438865]]],
    'GA': ['Gabon', [[8.79799563969, -4.97882659263, 14.4254557634, 2.32675751384]]],
    'GB': ['United Kingdom', [[-9.57216793459, 48.759999905, 2.78153079591, 61.6350001085]]],
    'GD': ['Grenada', [[ -62.813504, 10.989115, -60.363392, 13.540112]]],
    'GE': ['Georgia', [[39.9550085793, 41.0644446885, 46.6379081561, 43.553104153]]],
    'GG': ['Guernsey', [[-2.790948, 49.313433, -2.149365, 50.135901]]],
    'GH': ['Ghana', [[-3.24437008301, 4.71046214438, 1.0601216976, 11.0983409693]]],
    'GI': ['Gibraltar', [[-5.457244, 36.008739, -5.337133, 36.155070]]],
    'GL': ['Greenland', [[-76.297, 59.03676, -12.20855, 83.64513]]],
    'GM': ['Gambia', [[-17.8415246241, 12.1302841252, -13.8449633448, 13.8764918075]]],
    'GN': ['Guinea', [[-15.1303112452, 7.3090373804, -7.83210038902, 12.5861829696]]],
    'GP': ['Guadeloupe', [[-62.832560, 15.818848, -60.572362, 18.615294]]],
    'GQ': ['Equatorial Guinea', [[7.3056132341, 0.01011953369, 12.285078973, 3.28386607504], [5, -3, 7, 0]]],
    'GR': ['Greece', [[ 18.770911490759637, 34.65506302916286,  29.35545217588892, 42.29577743856077]]],
    'GS': ['South Georgia and South Sandwich Islands', [[-38.298695, -60.327394, -25.181020, -53.817812]]],
    'GT': ['Guatemala', [[-92.2292486234, 8.7353376327, -88.2250227526, 17.8193260767]]],
    'GW': ['Guinea Bissau', [[-18.6774519516, 10.0404116887, -13.7004760401, 12.6281700708]]],
    'GY': ['Guyana', [[-61.4103029039, 1.26808828369, -56.5393857489, 8.36703481692]]],
    'HN': ['Honduras', [[-89.3533259753, 12.9846857772, -82.147219001, 18.0054057886]]],
    'HR': ['Croatia', [[13.3569755388, 41.47999136, 19.3904757016, 46.5037509222]]],
    'HT': ['Haiti', [[-75.4580336168, 17.0309927434, -71.6248732164, 20.5156839055]]],
    'HU': ['Hungary', [[16.2022982113, 45.7594811061, 22.710531447, 48.6238540716]]],
    'ID': ['Indonesia', [[94.2930261576, -12.3599874813, 141.03385176, 7.47982086834]]],
    'IE': ['Ireland', [[-12.97708574059, 50.3693012559, -5.03298539878, 58.5316222195]]],
    'IL': ['Israel', [[34.2654333839, 29.5013261988, 35.8363969256, 33.2774264593]]],
    'IM': ['Isle of Man', [[-5.850942, 53.039203, -3.296132, 55.423695]]],
    'IN': ['India', [[67.1766451354, 6.56553477623, 97.4025614766, 35.4940095078]]],
    'IQ': ['Iraq', [[38.7923405291, 29.0990251735, 48.5679712258, 37.3852635768]]],
    'IR': ['Iran', [[44.1092252948, 24.0782370061, 63.3166317076, 39.7130026312]]],
    'IS': ['Iceland', [[-25.3261840479, 60.2763829617, -12.609732225, 67.9267923041]]],
    'IT': ['Italy', [[6.6499552751, 34.519987291, 18.4802470232, 47.1153931748]]],
    'JE': ['Jersey', [[-3.255378, 48.160392, -1.003782, 50.262766]]],
    'JM': ['Jamaica', [[-79.4377192858, 17.7011162379, -75.1996585761, 19.5242184514]]],
    'JO': ['Jordan', [[34.9226025734, 29.1974946152, 39.1954683774, 33.3786864284]]],
    'JP': ['Japan', [[122.408463169, 23.0295791692, 148.543137242, 46.5514834662]]],
    'KE': ['Kenya', [[33.8935689697, -4.67677, 41.8550830926, 5.506]]],
    'KG': ['Kyrgyzstan', [[69.464886916, 39.2794632025, 80.2599902689, 43.2983393418]]],
    'KH': ['Cambodia', [[102.3480994, 9.4865436874, 107.614547968, 14.5705838078]]],
    'KI': ['Kiribati', [[-176.228370, -12.899120, -149.525674, 5.309838], [168, -4, 178, 5]]],
    'KM': ['Comoros', [[40.188474, -13.463598, 46.608457, -10.321376]]],
    'KN': ['Saint Kitts and Nevis', [[-63.870331, 16.093414, -62.527695, 17.431763]]],
    'KP': ['North Korea', [[124.265624628, 37.669070543, 130.780007359, 42.9853868678]]],
    'KR': ['South Korea', [[123.117397903, 32.3900458847, 131.468304478, 39.6122429469]]],
    'KW': ['Kuwait', [[46.5687134133, 28.5260627304, 49.4160941913, 30.0590699326]]],
    'KY': ['Cayman Islands', [[-82.464856, 18.182946, -79.613660, 20.825009]]],
    'KZ': ['Kazakhstan', [[46.4664457538, 40.6623245306, 87.3599703308, 55.3852501491]]],
    'LA': ['Laos', [[100.115987583, 13.88109101, 107.564525181, 22.464531194]]],
    'LB': ['Lebanon', [[34.1260526873, 33.0890400254, 36.6117501157, 34.6449140488]]],
    'LC': ['St Lucia', [[-61.216819, 13.702059, -60.677914, 14.115870]]],
    'LI': ['Liechtenstein', [[9.455185, 47.046620, 9.629813, 47.275750]]],
    'LK': ['Sri Lanka', [[78.6951668639, 5.96836985923, 83.7879590189, 10.84407766361], [79.6444708682081, 9.470904842099836, 79.74474918772529, 9.555829147131542]]],
    'LR': ['Liberia', [[-11.4387794662, 3.35575511313, -7.53971513511, 8.54105520267]]],
    'LS': ['Lesotho', [[26.9992619158, -30.6451058896, 29.3251664568, -28.6475017229]]],
    'LT': ['Lithuania', [[20.0358004086, 53.9057022162, 26.5882792498, 56.3725283881]]],
    'LU': ['Luxembourg', [[5.67405195478, 49.4426671413, 6.54275109216, 50.1480516628]]],
    'LV': ['Latvia', [[19.0558004086, 55.61510692, 28.1767094256, 58.9701569688]]],
    'LY': ['Libya', [[9.31941084152, 19.58047, 25.16482, 33.1369957545]]],
    'MA': ['Morocco', [[-17.0204284327, 21.4207341578, -1.12455115397, 35.9999881048]]],
    'MC': ['Monaco', [[7.407828, 43.724330, 7.440444, 43.752297]]],
    'MD': ['Moldova', [[26.6193367856, 45.4882831895, 30.0246586443, 48.4671194525]]],
    'ME': ['Montenegro', [[18.45, 41.87755, 20.3398, 43.52384]]],
    'MF': ['Saint-Martin', [[-63.173560, 18.022431, -62.944875, 18.139666]]],
    'MG': ['Madagascar', [[41.2541870461, -27.6014344215, 52.4765368996, -10.0405567359]]],
    'MH': ['Marshall Island', [[159.842056, 3.845600, 172.740494, 12.814941]]],
    'MK': ['North Macedonia', [[20.46315, 40.8427269557, 22.9523771502, 42.3202595078]]],
    'ML': ['Mali', [[-12.1707502914, 10.0963607854, 4.27020999514, 24.9745740829]]],
    'MM': ['Myanmar', [[92.3032344909, 9.93295990645, 101.180005324, 28.335945136]]],
    'MN': ['Mongolia', [[87.7512642761, 41.5974095729, 119.772823928, 52.0473660345]]],
    'MQ': ['Martinique', [[-63.234232, 13.285308, -60.797525, 16.876946]]],
    'MR': ['Mauritania', [[-17.0634232243, 14.6168342147, -4.92333736817, 27.3957441269]]],
    'MS': ['Montserrat', [[-62.256975, 16.670934, -62.127199, 16.830380]]],
    'MT': ['Malta', [[13.166141, 35.715831, 15.590642, 37.081125]]],
    'MU': ['Mauritius', [[56.246428, -21.527530, 60.867156, -8.769458], [62.196815356054394, -20.83910465737219, 64.60345296734697, -19.62080881436224]]],
    'MV': ['Maldives', [[72.358411, -1.865774, 74.555676, 7.906712]]],
    'MW': ['Malawi', [[32.6881653175, -16.8012997372, 35.7719047381, -9.23059905359]]],
    'MX': ['Mexico', [[-119.12776, 14.5388286402, -85.491982388, 32.72083]]],
    'MY': ['Malaysia', [[99.085756871, 0.773131415201, 119.181903925, 7.92805288332]]],
    'MZ': ['Mozambique', [[30.1794812355, -26.7421916643, 42.7754752948, -10.3170960425]]],
    'NA': ['Namibia', [[11.7341988461, -29.045461928, 25.0844433937, -16.9413428687]]],
    'NC': ['New Caledonia', [[162.029605748, -23.3999760881, 168.120011428, -18.1056458473]]],
    'NE': ['Niger', [[0.295646396495, 11.6601671412, 15.9032466977, 23.4716684026]]],
    'NG': ['Nigeria', [[2.69170169436, 3.24059418377, 14.5771777686, 13.8659239771]]],
    'NI': ['Nicaragua', [[-87.6684934151, 10.7268390975, -82.147219001, 15.0162671981]]],
    'NL': ['Netherlands', [[2.31497114423, 50.803721015, 7.29205325687, 54.5104033474]]],
    'NO': ['Norway', [[3.99207807783, 57.0788841824, 33.29341841, 73.21311908]]],
    'NP': ['Nepal', [[80.0884245137, 26.3978980576, 88.1748043151, 30.4227169866]]],
    'NR': ['Nauru', [[165.9007475834, -1.5573764007, 168.9685492693, 1.4984335412]]],
    'NU': ['Niue', [[-170.954904, -20.160813, -169.762987, -18.948258]]],
    'NZ': ['New Zealand', [[160, -47, 180, -32], [-180, -47, -170, -32]]],
    'OM': ['Oman', [[51.0000098, 16.6510511337, 60.8080603372, 26.3959343531]]],
    'PA': ['Panama', [[-82.9657830472, 6.9205414901, -77.2425664944, 10.61161001224]]],
    'PE': ['Peru', [[-81.6109425524, -18.3479753557, -68.6650797187, -0.0572054988649]]],
    'PG': ['Papua New Guinea', [[140.000210403, -13.6524760881, 156.019965448, -0.50000212973]]],
    'PH': ['Philippines', [[116.17427453, 4.58100332277, 127.537423944, 21.5052273625]]],
    'PK': ['Pakistan', [[60.8742484882, 23.6919650335, 77.8374507995, 37.1330309108]]],
    'PL': ['Poland', [[14.0745211117, 49.0273953314, 24.0299857927, 56.8515359564]]],
    'PR': ['Puerto Rico', [[-68.2424275377, 17.946553453, -65.5910037909, 20.5206011011]]],
    'PS': ['West Bank', [[34.9274084816, 31.3534353704, 35.5456653175, 32.5325106878]]],
    'PS': ['Palestine', [[33.161353, 31.036574, 35.864234, 32.824322]]],
    'PT': ['Portugal', [[-11.72657060387, 36.838268541, -6.3890876937, 42.280468655], [-19.451724962564013, 29.401532401650364, -15.048078338508628, 34.13531220458579], [-32.47751352524867, 36.137579870831885, -21.469213296357385, 40.763624391184145]]],
    'PY': ['Paraguay', [[-62.6850571357, -27.5484990374, -54.2929595608, -19.3427466773]]],
    'QA': ['Qatar', [[50.7439107603, 24.5563308782, 52.6067004738, 26.1145820175]]],
    'RE': ['Reunion', [[54.206600, -23.375728, 57.356996, -20.667645]]],
    'RO': ['Romania', [[20.2201924985, 43.6884447292, 30.62654341, 48.2208812526]]],
    'RS': ['Serbia', [[18.82982, 42.2452243971, 22.9860185076, 46.1717298447]]],
    'RU': ['Russia', [[26.822680, 40.483493, 180, 81.903807], [-180, 61, -169, 72], [19.489414671469504, 54.33182221678806, 22.905639654213825, 55.31413673335722]]],
    'RW': ['Rwanda', [[29.0249263852, -2.91785776125, 30.8161348813, -1.13465911215]]],
    'SA': ['Saudi Arabia', [[34.6323360532, 15.3478913436, 55.6666593769, 32.161008816]]],
    'SB': ['Solomon Islands', [[155.391357864, -13.8263672828, 170.398645868, -6.49933847415]]],
    'SC': ['Seychelles', [[54.174998, -6.822535, 57.007276, -3.546368]]],
    'SD': ['Sudan', [[21.93681, 8.61972971293, 38.4100899595, 23.0], [31.309568631189364, 22.0, 31.51105877462657, 22.228282131067726]]],
    'SE': ['Sweden', [[10.0273686052, 54.2617373725, 24.9033785336, 69.1062472602]]],
    'SG': ['Singapore', [[103.570233, 1.158152, 104.097863, 1.468348]]],
    'SH': ['Saint Helena', [[-17.8169342584, -38.0372386419, -4.6134693669, -7.8971012947]]],
    'SI': ['Slovenia', [[13.367471, 45.418064, 16.618664, 46.884908]]],
    'SK': ['Slovakia', [[16.8799829444, 47.7484288601, 22.5581376482, 49.5715740017]]],
    'SL': ['Sierra Leone', [[-13.2465502588, 6.78591685631, -10.2300935531, 10.0469839543]]],
    'SM': ['San Marino', [[12.401383, 43.893395, 12.521954, 43.993838]]],
    'SN': ['Senegal', [[-18.6250426905, 11.332089952, -11.4678991358, 16.5982636581]]],
    'SO': ['Somalia', [[40.98105, -3.68325, 51.13387, 12.02464]]],
    'SR': ['Suriname', [[-58.0446943834, 1.81766714112, -53.9580446031, 6.0252914494]]],
    'SS': ['South Sudan', [[23.8869795809, 3.50917, 35.2980071182, 12.2480077571]]],
    'ST': ['Sao Tome and Principe', [[5.372594, -1.065411, 10.790074, 2.439956]]],
    'SV': ['El Salvador', [[-91.0955545723, 12.1490168319, -87.7235029772, 14.4241327987]]],
    'SX': ['Sint Maarten', [[-64.160383, 17.909370, -62.003557, 18.063344]]],
    'SY': ['Syria', [[35.7007979673, 32.312937527, 42.3495910988, 37.2298725449]]],
    'SZ': ['Eswatini', [[30.6766085141, -27.2858794085, 32.0716654803, -25.660190525]]],
    'TC': ['Turks and Caicos Islands', [[-73.515351, 20.176436, -70.111847, 23.973323]]],
    'TD': ['Chad', [[13.5403935076, 7.42192454674, 23.88689, 23.40972]]],
    'TF': ['Fr. S. and Antarctic Lands', [[68.72, -50.775, 72.56, -47.625]]],
    'TG': ['Togo', [[-0.0497847151599, 5.92883738853, 1.86524051271, 11.0186817489]]],
    'TH': ['Thailand', [[97.3758964376, 5.69138418215, 105.589038527, 20.4178496363]]],
    'TJ': ['Tajikistan', [[67.4422196796, 36.7381712916, 74.9800024759, 40.9602133245]]],
    'TK': ['Tokelau', [[-173.534264, -11.492260, -170.059350, -8.485807]]],
    'TL': ['East Timor', [[124.968682489, -9.39317310958, 127.335928176, -8.27334482181]]],
    'TM': ['Turkmenistan', [[51.5024597512, 35.2706639674, 66.5461503437, 42.7515510117]]],
    'TN': ['Tunisia', [[7.52448164229, 30.3075560572, 12.4887874691, 39.3499944118]]],
    'TO': ['Tonga', [[-176.986604, -22.027399, -172.069058, -14.410732]]],
    'TR': ['Turkey', [[25.60417275656444, 35.27139944988264, 47.7939896991, 42.1414848903]]],
    'TT': ['Trinidad and Tobago', [[-62.95, 9.0, -59.895, 12.89]]],
    'TV': ['Tuvalu', [[175.014362906, -11.134731836, 180, -4.002830727]]],
    'TW': ['Taiwan', [[118.106188593, 21.9705713974, 122.951243931, 26.2954588893]]],
    'TZ': ['Tanzania', [[29.3399975929, -11.7209380022, 42.31659, -0.95]]],
    'UA': ['Ukraine', [[22.0856083513, 43.2614785833, 40.0807890155, 52.3350745713]]],
    'UG': ['Uganda', [[29.5794661801, -1.44332244223, 35.03599, 4.24988494736]]],
    'US': ['United States', [[-127.60300365652778, 23.328307850864494, -64.80508473115059, 49.1844355407274], [-160.82810044701534, 18.30244581034809, -153.59304286436185, 22.489114511005596], [-190.60787503833, 50.95801418800582, -130.4491456421077, 72.56926153367206], [171, 50, 180, 62]]],
    'UY': ['Uruguay', [[-58.4270741441, -35.0526465797, -52.209588996, -30.1096863746]]],
    'UZ': ['Uzbekistan', [[55.9289172707, 37.1449940049, 73.055417108, 45.5868043076]]],
    'VA': ['Vatican City', [[12.445713,41.900179,12.458437,41.9074918]]],
    'VC': ['St Vincent and the Grenadines', [[-63.488755, 12.513980, -60.104166, 13.597771]]],
    'VE': ['Venezuela', [[-73.3049515449, 0.724452215982, -59.7582848782, 12.1623070337]]],
    'VG': ['British Virgin Islands', [[-65.862530, 17.300936, -63.262402, 19.759272]]],
    'VN': ['Vietnam', [[102.170435826, 7.59975962975, 114.33526981, 23.3520633001]]],
    'VU': ['Vanuatu', [[165.77076852020062, -20.465046828827884, 170.84645193920196, -12.744244960446533]]],
    'WS': ['Samoa', [[-173.850164, -14.081769, -171.309332, -12.404114]]],
    'XK': ['Kosovo', [[20.023050, 41.851277, 21.791849, 43.271330]]],
    'YE': ['Yemen', [[41.6048726743, 11.5859504257, 55.1085726255, 19.0000033635]]],
    'YT': ['Mayotte', [[44.005064, -13.012022, 45.319548, -11.631733]]],
    'ZA': ['South Africa', [[15.3449768409, -35.8191663551, 34.830120477, -22.0913127581]]],
    'ZM': ['Zambia', [[21.887842645, -17.9612289364, 33.4856876971, -8.23825652429]]],
    'ZW': ['Zimbabwe', [[25.2642257016, -22.2716118303, 32.8498608742, -15.5077869605]]],
    'SJ': ['Svalbard and Jan Mayen', [[8.04687789766614, 74.35498023304599, 34.306805275624086, 80.81809323746566], [-11, 70, -6, 73]]],
    'AS': ['American Samoa', [[-172.8610098435224, -15.38536238983563, -167.5262297667812, -10.226237921088725]]],
    'BL': ['Saint Barthelemy', [[-62.920134746383596, 17.874249226856882, -62.781361781310444, 17.962748324810512]]],
    'PW': ['Palau', [[130.85241878355825, 2.276788844461931, 135.76330741590354, 8.605929299211784]]],
    'GU': ['Guam', [[143.37910069285803, 12.074077183069257, 146.2219837083251, 14.871093966229127]]],
    'NF': ['Norfolk Island', [[167.88255366736797, -29.154067146012604, 168.04076064851756, -28.96378963203278]]],
    'AX': ['Aland Islands', [[19.41546265377435, 59.89282758281474, 21.155608234093492, 60.61358224907711]]],
    'PF': ['French Polynesia', [[-154.8492413037696, -28.504696574791765, -134.457641544589, -7.824286674613189]]],
    'CX': ['Christmas Island', [[104.48128775611971, -11.593626050771782, 107.82194885638076, -9.36567389228022]]],
    'GF': ['French Guiana', [[-54.92354908094463, 2.00435778305043, -50.60425902538684, 6.2031436447261115]]],
    'UM': ['U.S. Outlying Islands', [[-177.54357916904053, -2.15187972655016452, -175.4280923793453, 2.2611789926758716], [-177.66845835922342, -1.7755604617716081, -175.55966214239578, 1.8972037618508617], [-161.08419013026827, -1.44358674371116674, -159.9215370087966, 0.28433561526771733], [-171.60070526174863, 16.666959794330396, -168.4084445151895, 18.809648630665933], [-162.48666106672582, 6.317318203657856, -162.25802321898195, 6.490972336536874], [-178.8221773841471, 27.813335006862395, -176.08222739702043, 28.474723496303916], [-163.07344090462308, 5.416805566194564, -160.9969079203459, 7.094568752973269], [165.54184201409905, 18.22422645531609, 168.72625303616525, 20.361017715618065], [-76.09455677285277, 17.3288618974045, -74.91396900019187, 18.476108088350912]]],
    'PM': ['Saint Pierre and Miquelon', [[-58.55988810425815, 46.670038102461234, -56.03887678894177, 48.21031904136765]]],
    'MP': ['Northern Mariana Islands', [[144.5463565403477, 13.755149291327577, 146.55286166897886, 20.22328055806068]]],
    'PN': ['Pitcairn Islands', [[-131.2786971323431, -26.191081882312368, -126.52127533737676, -23.496568171277936]]],
    'VI': ['U.S. Virgin Islands', [[-65.14144720065221, 16.59356648536139, -64.42179451575198, 18.503975380017405]]],
    'IO': ['British Indian Ocean Territory', [[70.96050171797329, -7.786586947187489, 73.04999870090312, -6.129418349393616]]],
    'CC': ['Cocos (Keeling) Islands', [[96.62290317160732, -12.32215588218224, 97.13337704832878, -11.70764682942696]]],
    'WF': ['Wallis and Futuna', [[-179.1198075001247, -15.998515007293918, -174.97142472520295, -12.265828002490087]]],
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
  'Federated States of Micronesia': 'FM',
  'Cocos Islands': 'CC'
}

small_countries_dict = {
  '17,-62': ['KN', 'Saint Kitts and Nevis'],
  '36,-5': ['GI', 'Gibraltar'],
  '-19,63': ['MU', 'Mauritius'],
  '47,9': ['LI', 'Liechtenstein'],
  '43,7': ['MC', 'Monaco'],
  '41,12': ['VA', 'Vatican City'],
  '15,-61': ['DM', 'Dominica'],
  '22,31': ['SD', 'Sudan'],
  '-10,105': ['CX', 'Christmas Island'],
  '9,79': ['LK', 'Sri Lanka'],
  '43,12': ['SM', 'San Marino'],
  '0,-176': ['UM', 'U.S. Outlying Islands'],
  '35,-5': ['ES', 'Spain'],
  '6,-162': ['UM', 'U.S. Outlying Islands'],
  '16,-62': ['MS', 'Montserrat'],
  '42,1': ['AD', 'Andorra'],
}
