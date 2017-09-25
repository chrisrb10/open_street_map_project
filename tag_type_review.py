# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# toggle between full and sample file by commenting in / out lines below

#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'

# RE codes to capture tag types
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+')        #(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'\"\?%#$@\,\. \t\r\n]')
naptan = re.compile(r'^(naptan:|Naptan:)[a-zA-Z]*$')




# comment in / out the print statements below to see a list of the tag types identified for each of the RE codes above

def key_type(element, keys):
    n=0
    #print (element, keys)
    #print ('before tag test',element.attrib)
    if element.tag == "tag":
        if naptan.search(element.attrib['k']):
            keys['naptan'] +=1
            #print 'found naptan:', element.attrib['k']

        elif lower.search(element.attrib['k']):
            #print 'found lower:', element.attrib['k']
            keys['lower'] +=1

        elif lower_colon.search(element.attrib['k']):
            #print 'found lower_colon:', element.attrib['k']
            keys['lower_colon'] +=1

        elif problemchars.search(element.attrib['k']):
            #print 'found problemchars:', element.attrib['k']
            keys['problemchars'] +=1
        else:
            #print 'found other:', element.attrib['k'].lower()
            keys['other']+=1

    return keys


    
# NOTE use n count and break to test script on short sequences before running on full file

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0, 'naptan':0}
    n=0
    for _, element in ET.iterparse(filename):
        n+=1
        #if n>20000: break
        #print (n, _, element)
        keys = key_type(element, keys)

    return keys



if __name__ == "__main__":
    keys = process_map(OSM_FILE)
    pprint.pprint(keys)
