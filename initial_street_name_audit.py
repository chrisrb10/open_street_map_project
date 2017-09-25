# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# An initial audit of street types, to see what types of names are present.

#osm_file = open("swlondon_sample.osm", "r")
osm_file = open("swlondon.osm", "r")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    #print street_name
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print ("%s: %d" % (k, v) )

def is_street_name(elem):

    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    #n = 0
    for event, elem in ET.iterparse(osm_file):
        #if n>20: break
        if is_street_name(elem):
            #n+=1
            audit_street_type(street_types, elem.attrib['v'])
    print_sorted_dict(street_types)

if __name__ == '__main__':
    audit()
