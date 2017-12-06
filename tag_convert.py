##############################################################################
# functions used to convert xml data to dictionary format for writing to csv #
##############################################################################

# this function takes in a dictionary returned from the fix_full_address function and converts it into separate
# tag dictionaries depending on its parameter with the node id and type already defined
def convert_to_tag(el_id, key, addr_dict):
    tag_to_return = { "id": el_id,
                      "type": 'addr'
                      }
    if key == 'state':
        tag_to_return['key'] = 'state'
        tag_to_return['value'] = 'MA'
    elif key == 'city':
        tag_to_return['key'] = 'city'
        tag_to_return['value'] = 'Boston'
    elif key == 'zip':
        tag_to_return['key'] = 'postcode'
        tag_to_return['value'] = addr_dict[key]
    elif key == 'street':
        tag_to_return['key'] = 'street'
        tag_to_return['value'] = addr_dict[key]
    elif key == 'housenumber':
        tag_to_return['key'] = 'housenumber'
        tag_to_return['value'] = addr_dict[key]
    else:
        return None
    return tag_to_return
