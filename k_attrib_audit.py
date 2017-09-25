# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint




#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'


def process_map(filename):
    tag_ks = defaultdict(int)
    n=0
    for _, element in ET.iterparse(filename):
        n+=1
        #if n>20000: break
        #print (n, _, element)
        if element.tag == "tag":
            tag_ks[element.attrib['k']] += 1


    return tag_ks


if __name__ == "__main__":
    tag_keys = process_map(OSM_FILE)
    pprint.pprint(sorted(tag_keys.items() , key=lambda x: x[1], reverse=True))
