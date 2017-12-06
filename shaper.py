'''
The shape element function is used to take each tag element in the XML dataset, determine if it is
a node or a way, and clean and shape the data depending on what it finds. It relies on the
cleaner functions from the clean_functions file.
'''

import re
from tag_convert import convert_to_tag, return_secondary_tag
from clean_functions import *

# variables

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# regex variables

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    # variable used to determine if a full address needs to be split into multiple address segments
    split_tags = False

    # YOUR CODE HERE
    if element.tag == 'node':
        for attb in element.attrib:
            if attb in NODE_FIELDS:
                node_attribs[attb] = element.attrib[attb]
        for tag in element.iter("tag"):
            # iterate through each tag under a node element
            secondary_tag = {}
            secondary_tag['id'] = node_attribs['id']
            if tag.attrib['k']:
                key = tag.attrib['k']
                # if problem characters are found, pass
                if PROBLEMCHARS.search(key):
                    pass
                elif LOWER_COLON.search(key):
                    # if colon is found in key, split on colon, set first item as type and second item as key
                    k_type = key.split(":",1)[0]
                    key = key.split(":",1)[1]
                    secondary_tag['key'] = key
                    secondary_tag['type'] = k_type
                    if key == 'city':
                        # if key is city, check and make sure the city is Boston
                        if is_boston(tag.attrib['v']):
                            secondary_tag['value'] = tag.attrib['v']
                        else:
                            continue
                    elif key == 'postcode':
                        # if key is postcode, check and make sure zip code is a valid Boston postal code
                        zip_code = update_zip_code(tag.attrib['v'], boston_zips)
                        if zip_code == None:
                            continue
                        else:
                            secondary_tag['value'] = zip_code
                    elif key == 'street':
                        # if key is street, run street through update_street_name function to transform
                        # any common abbreviations into full names
                        street = update_street_name(tag.attrib['v'], street_mapping)
                        secondary_tag['value'] = street
                elif tag.attrib['k'] == 'address':
                    # if key is full address, split address into separate keys in a dictionary using
                    # fix_full_address function
                    split_tags = True
                    addr_dict = fix_full_address(tag.attrib['v'])
                    if addr_dict == None:
                        # if dictionary came back invalid, continue to next iteration of loop
                        continue
                    else:
                        for field in addr_dict:
                            # convert each key in the dictionary to its own tag and append it to tags
                            new_tag = convert_to_tag(node_attribs['id'], field, addr_dict)
                            if new_tag['value'] == None:
                                continue
                            else:
                                tags.append(new_tag)
                else:
                    # if none of the above conditions apply, set the values of secondary_tag below
                    secondary_tag['key'] = key
                    secondary_tag['type'] = "regular"
                    secondary_tag['value'] = tag.attrib['v']
                    tags.append(secondary_tag)
            if split_tags == False:
                # if we did not change split_tags to True, need to still append the tag
                tags.append(secondary_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        # set position for way nodes at 0 for each way element
        position = 0
        for attb in element.attrib:
            if attb in WAY_FIELDS:
                way_attribs[attb] = element.attrib[attb]
        for tag in element.iter("tag"):
            # iterate through each tag under a node element
            secondary_tag = {}
            secondary_tag['id'] = way_attribs['id']
            if tag.attrib['k']:
                key = tag.attrib['k']
                if PROBLEMCHARS.search(key):
                    # if any problem characters are found, continue to next loop iteration
                    continue
                # if colon is found in key, split on colon, set first item as type and second item as key
                elif LOWER_COLON.search(key):
                    k_type = key.split(":",1)[0]
                    key = key.split(":",1)[1]
                    secondary_tag['key'] = key
                    secondary_tag['type'] = k_type
                    if key == 'city':
                        # if key is city, check and make sure the city is Boston
                        if is_boston(tag.attrib['v']):
                            secondary_tag['value'] = tag.attrib['v']
                        else:
                            continue
                    elif key == 'postcode':
                        # if key is postcode, check and make sure zip code is a valid Boston postal code
                        zip_code = update_zip_code(tag.attrib['v'], boston_zips)
                        if zip_code == None:
                            continue
                        else:
                            secondary_tag['value'] = zip_code
                    elif key == 'street':
                        # if key is street, run street through update_street_name function to transform
                        # any common abbreviations into full names
                        street = update_street_name(tag.attrib['v'], street_mapping)
                        secondary_tag['value'] = street
                elif tag.attrib['k'] == 'address':
                    # if key is full address, split address into separate keys in a dictionary using
                    # fix_full_address function
                    split_tags = True
                    addr_dict = fix_full_address(tag.attrib['v'])
                    if addr_dict == None:
                        # if dictionary came back invalid, continue to next iteration of loop
                        continue
                    else:
                        for field in addr_dict:
                            # convert each key in the dictionary to its own tag and append it to tags
                            new_tag = convert_to_tag(way_attribs['id'], field, addr_dict)
                            if new_tag['value'] == None:
                                continue
                            else:
                                tags.append(new_tag)
                else:
                    # if none of the above conditions apply, set the values of secondary_tag below
                    secondary_tag['key'] = key
                    secondary_tag['type'] = "regular"
                    secondary_tag['value'] = tag.attrib['v']
                    tags.append(secondary_tag)
            if split_tags == False:
                # if we did not change split_tags to True, need to still append the tag
                tags.append(secondary_tag)
        for tag in element.iter("nd"):
            nd_elems = {}
            nd_elems['id'] = way_attribs['id']
            nd_elems['node_id'] = tag.attrib['ref']
            nd_elems['position'] = position
            position += 1
            way_nodes.append(nd_elems)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
