# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint




# Does a count of element types in osm data file

#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'

# NOTE use n count and break to test script on short sequences before running on full file


tag_types = {}
context = ET.iterparse(OSM_FILE, events=('end',))
#_, root = next(context)
n = 0
for event, elem in context:
    n+=1
    #if n>2000: break
    #print (event, elem)
    if event == 'end':
        tag_types[elem.tag] = tag_types.get(elem.tag,0)+1


print 'Final n= ',n,'\n\n',tag_types
