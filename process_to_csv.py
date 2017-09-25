# import required moduls & dinctionaries

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import csv
import codecs
import cerberus
import schema
import time

import sqlite3

import schema

SCHEMA = schema.schema

# Input file
#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'

#########################################
## STREET NAME CLEANING CODE & FUNCTIONS
#########################################

expected = ['Approach','Avenue','Bank','Boulevard','Bridge','Broadway','Buildings','Causeway','Centre',
            'Chase','Close','Common','Copse','Corner','Cottages','Court','Crescent','Croft',
           'Crossway','Cutting','Deep','Drive','East', 'Embankment','Gardens','Green','Grove','Heath','Hill',
            'Heights','Lane','Mall','Meadows','Mews','North','Path','Parade','Park','Place','Quadrant','Quay',
            'Rise','Road','Row', 'South','Square','Street','Terrace','Vale','Villas','Walk','Way','West']


name_mapping = { 'St': 'Street',
            'St.': 'Street',
            'Strreet': 'Street',
            'street': 'Street',
            'Rd.':'Road',
            'Rd' : 'Road',
            'ROAD':'Road',
            'road':'Road',
            'Ave':'Avenue',
            'Avenuen':'Avenue',
            'lane': 'Lane',
            'park':'Park'
            } # etc. to be updated


problem_street_names = ['11', '218','24', 'Rectory Grove Hampton TW12 1EG','Fulham Road, Chelsea',
                        'Sheffield Rd, Heathrow Airport (LHR)','Beacon Rd (Entrance Sanctuary Rd)',
                        'Wimbledon']

change_list_mapping = { 'Rectory Grove Hampton TW12 1EG': 'Rectory Grove',
                        'Sheffield Rd, Heathrow Airport (LHR)': 'Sheffield Road',
                        'Beacon Rd (Entrance Sanctuary Rd)': 'Beacon Road',
                        'Fulham Road, Chelsea': 'Fulham Road',
                        'Wimbledon' : 'Wimbledon Hill Road'}

drop_list = ['11', '218','24']


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def update_name(name):
    #print (name.split()[-1])
    if name in drop_list:
        return 'DROP TAG'
    if name in change_list_mapping:
        name = change_list_mapping[name]
        return name
    name_list = name.split()
    try:
        name_list[-1] = name_mapping[name_list[-1]]
        name_list[0] = name_list[0].title()
        return ' '.join(name_list)
    except:
        return name

########################################
# Code for cleaning problem tag types
########################################

problem_tag_list = ['bus:lanes:backward', 'bus:lanes:forward','psv:lanes',
                    'motorcycle:lanes:forward','psv:lanes:backward',
                    'psv:lanes:forward']

tag_type_mapping = {'bus:lanes:backward':'lanes:bus:backward',
                    'bus:lanes:forward' : 'lanes:bus:forward',
                    'motorcycle:lanes:forward' : 'lanes:motorcycle:forward',
                    'psv:lanes': 'lanes:psv',
                    'psv:lanes:backward': 'lanes:psv:backward',
                    'psv:lanes:forward' : 'lanes:psv:forward'
                    }


def is_problem_type(elem):
    return (elem.attrib['k'] in problem_tag_list)


def update_tag_type(tag_type):
    if tag_type in tag_type_mapping:
        tag_type = tag_type_mapping[tag_type]
        return tag_type

#####################################
# Code for cleaning postcode problem
####################################

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")



def clean_postcode(code):
    if ';' in code:
        print 'CLEANING A POSTCODE:', code
        code = code.split(';')[0]
        print 'NEW POSTCODE:', code
    return code


# Ouput file naming

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"


# re expressions as used in code
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
NAPTAN = re.compile(r'^(naptan:|Naptan:)[a-zA-Z]*$')



# fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



# A function to shape the tags and add to the relevant dict objects.
# Used for both nodes and way tags - as treatment is the same.
# Takes list of desired tag fields (from NODE_TAGS_FIELDS)
# For id (an attrb from parent node or way and NOT in tag), parent node / way id is returned
# for 'key' checks if:
#                      a PROBLEMCHARS match, and ignores / drops
#                      a LOWER_COLON or NAPTAN match and splits, extracts / sets type (text before :)
#                                        and returns rest as key
#                       (NOTE - type is 'regular' if no other found)
# added .lower() on tag_dict type & field setting to remove block capital inconsistencies etc.

def shape_tags(element, id_number, tag_attr_fields = NODE_TAGS_FIELDS,
                   problem_chars=PROBLEMCHARS, lower_colon=LOWER_COLON,
                   naptan=NAPTAN, default_tag_type='regular'):
    tag_dict={}
    for field in tag_attr_fields:
        # manage id number (from parent node / way)
        if field == 'id':
            tag_dict[field]= id_number

        # process 'keys'
        elif field == 'key':
            tag_dict['type'] = default_tag_type
            if problem_chars.search(element.attrib['k']):
                print 'IGNORING A TAG - PROBLEM CHARS', element.attrib['k']
                tag_dict={}
                return None
            elif lower_colon.search(element.attrib['k']) or naptan.search(element.attrib['k']):
                k = element.attrib['k']
                if is_problem_type(element):
                    print 'FOUND A PROBLEM TAG TYPE:', k
                    k = update_tag_type(k)
                    print 'CHANGED TO:', k

                split_k =  k.lower().split(':')
                tag_dict['type'] = split_k[0]
                tag_dict[field] = ':'.join(split_k[1:])
            else:
                tag_dict[field]= element.attrib['k'].lower()

        # process values (and calls on cleaning)
        elif field == 'value':
            if is_street_name(element):
                original_name = element.attrib['v']
                cleaned_name = update_name(original_name)
                if cleaned_name != original_name:
                    print ('CLEAN STREET NAME:', original_name, "=>", cleaned_name)
                    if cleaned_name == 'DROP TAG':
                        print 'DROPPING TAG FROM:', id_number
                        tag_dict={}
                        return None
                    tag_dict[field] = cleaned_name
                    continue
                else:
                    tag_dict[field] = original_name
                    continue

            elif is_postcode(element):
                tag_dict[field] = clean_postcode(element.attrib['v'])
                continue

            else:
                tag_dict[field]= element.attrib['v']

    return tag_dict


# shapes way nodes
def shape_way_nodes(element, id_number, position, way_node_fields=WAY_NODES_FIELDS):
    way_node_dict = {}
    for field in way_node_fields:
        if field == 'id':
            way_node_dict[field]= id_number
        elif field == 'position':
            way_node_dict[field]= position
        elif field == 'node_id':
            way_node_dict[field]= element.attrib['ref']
    return way_node_dict


# main shape element function - calls on shape tags and shapes way nodes
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for field in node_attr_fields:
            node_attribs[field]= element.attrib[field]
            id_number = element.attrib['id']
        for tag in element.iter('tag'):
            tag_dict = shape_tags(tag, id_number)
            if tag_dict is not None:
                tags.append(tag_dict)
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field]= element.attrib[field]
            id_number = element.attrib['id']
        for tag in element.iter('tag'):
            tag_dict = shape_tags(tag, id_number)
            if tag_dict is not None:
                tags.append(tag_dict)
        position = 0
        for way_node in element.iter('nd'):
            way_nodes.append(shape_way_nodes(way_node, id_number, position))
            position += 1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])



if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_FILE, validate=False)
