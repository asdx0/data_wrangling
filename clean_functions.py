########################################################
# functions used to clean address fields from xml data #
########################################################
import re

# variables used to compare data against for zip codes and street names
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

boston_zips = ['02163', '02199', '02203', '02205', '02208', '02210', '02215',
               '02222', '02228', '02283', '02284', '02455']
for i in range(101, 137):
    boston_zips.append("02" + str(i))

street_mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave.": "Avenue",
            "Ave": "Avenue",
            "Cambrdige": "Cambridge",
            "Ct": "Court",
            "Dr": "Drive",
            "HIghway": "Highway",
            "Pkwy": "Parkway",
            "Pl": "Plaza",
            "Rd": "Road",
            "ST": "St"
            }

# returns True if element is a street and False otherwise
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# returns True if element is a zip code and False otherwise
def is_postal(elem):
    return (elem.attrib['k'] == "addr:postcode")

# returns True if string parameter is Boston and False otherwise
def is_boston(city):
    return (city == 'Boston')

# checks if street name uses any abbreviations and if so returns an unabbreviated version
# else returns the original name
def update_street_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        last_word = name.split(" ")[-1]
        if last_word in mapping:
            return name.replace(last_word, mapping[last_word])
        else:
            return name
# splits zipcode on - to remove the last 4 digits if they are present and then verifies the zip against the
# list of valid Boston zip codes
def update_zip_code(zip_code, zip_list):
    new_zip = zip_code.split("-")[0]
    if new_zip not in zip_list:
        return None
    else:
        return new_zip

# takes a string full address as an input and returns a dictionary with separate address keys zip, state, city,
# street, and housenumber
def fix_full_address(addr):
    addr_dict = {}
    addr_list = addr.split(" ")
    for i in range(0, len(addr_list)):
        addr_list[i] = addr_list[i].replace(',', '')
    # validates zip code against update_zip_code function
    addr_dict['zip'] = update_zip_code(addr_list[-1], boston_zips)
    # only returns value if state is equal to MA -- cannot be part of Boston otherwise
    if addr_list[-2]  == "MA":
        addr_dict['state'] = "MA"
    else:
        return None
    # only returns value if city is equal to Boston -- cannot be part of Boston otherwise
    if addr_list[-3] == "Boston":
        addr_dict['city'] = "Boston"
    else:
        return None
    # checks if first field is a number
    # if first field number, store that as the housenumber and the remaining items between 0 and -3 (city)
    # as the street name
    try:
        addr_int = int(addr_list[0])
        addr_dict['housenumber'] = addr_list[0]
        # concatenates street name together and strips trailing space
        street_name = ""
        for x in range(1, len(addr_list) - 3):
            street_name += addr_list[x] + " "
        addr_dict['street'] = street_name.strip()
    # if first field not number, takes items 0 through -3 (city) as street name
    except:
        # concatenates street name together and strips trailing space
        street_name = ""
        for x in range(0, len(addr_list) - 3):
            street_name += addr_list[x] + " "
        addr_dict['street'] = street_name.strip()
    return addr_dict
