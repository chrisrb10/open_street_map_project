# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# Auditing Street Names


#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# expected street types list
expected = ['Approach','Avenue','Bank','Boulevard','Bridge','Broadway','Buildings','Causeway','Centre',
            'Chase','Close','Common','Copse','Corner','Cottages','Court','Crescent','Croft',
           'Crossway','Cutting','Deep','Drive','East', 'Embankment','Gardens','Green','Grove','Heath','Hill',
            'Heights','Lane','Mall','Meadows','Mews','North','Path','Parade','Park','Place','Quadrant','Quay',
            'Rise','Road','Row', 'South','Square','Street','Terrace','Vale','Villas','Walk','Way','West']



# mapping of street type errore / abbreviations to full type
mapping = { 'St': 'Street',
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


# list of 'problem' street names identified during process
problem_street_names = ['11', '218','24', 'Rectory Grove Hampton TW12 1EG','Fulham Road, Chelsea',
                        'Sheffield Rd, Heathrow Airport (LHR)','Beacon Rd (Entrance Sanctuary Rd)',
                        'Wimbledon']

# chenge mapping for problem street names
change_list_mapping = { 'Rectory Grove Hampton TW12 1EG': 'Rectory Grove',
                        'Sheffield Rd, Heathrow Airport (LHR)': 'Sheffield Road',
                        'Beacon Rd (Entrance Sanctuary Rd)': 'Beacon Road',
                        'Wimbledon' : 'Wimbledon Hill Road'}

# street name tags to drop
drop_list = ['11', '218','24']



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_problem_name(street_name, problems):
    return (street_name in problems)

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    n=0
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        n+=1
        #if n>20000: break
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter('tag'):
                if is_street_name(tag):
                    # Used code below to examine 'problem' street names in detail
                    #if is_problem_name(tag.attrib['v'], problem_street_names):

                        #print '\n',elem.tag
                        #for tag in elem.iter():
                            #print tag.attrib
                            #continue
                        #continue

                    audit_street_type(street_types, tag.attrib['v'])


    osm_file.close()
    return street_types


def update_name(name, mapping):
    #print (name.split()[-1])
    if name in drop_list:
        return 'DROP TAG'
    if name in change_list_mapping:
        name = change_list_mapping[name]
        return name
    name_list = name.split()
    try:
        name_list[-1] = mapping[name_list[-1]]
        name_list[0] = name_list[0].title()
        return ' '.join(name_list)
    except:
        return name


def propose_name(st_types):
    #st_types = audit(OSM_FILE)
    #assert len(st_types) == 3
    #pprint.pprint(dict(st_types))
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            if better_name != name:
                print (name, "=>", better_name)



if __name__ == '__main__':
    st_types = audit(OSM_FILE)
    propose_name(st_types)
    print '\n\n'
    #pprint.pprint(dict(st_types))
