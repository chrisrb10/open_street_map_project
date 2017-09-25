# import required modules & functions

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#OSM_FILE = 'swlondon_sample.osm'
OSM_FILE = 'swlondon.osm'

code_ingroup_re = re.compile(r'^[a-zA-Z]', re.IGNORECASE)


expected = []


#splits  postcode into outgroup & ingroup, adds ingroups to a 'set' of ingroups for each outgroup
#adds count to occurances of outgroup

def audit_postcode(postcode_outgroups, postcodes, code):
    # test on ';' added to deal with postcode data point containing ';' separated list
    if ';' in code:
        code = code.split(';')[0]
    code_sep = code.split()
    code_outgroup = code_sep[0]
    postcode_outgroups[code_outgroup] +=1
    if len(code_sep) == 2:
            postcodes[code_sep[0]].add(code_sep[1])
            return
    # code below purely to deal with one example found of multiple(2) postcodes separated by ;
    if len(code_sep)>2:
        print 'still have code_sep >2', code_sep
        code_1 = code.split(';')[0]
        code_sep = code_1.split()
        code_outgroup = code_sep[0]
        postcode_outgroups[code_outgroup] +=1
        postcodes[code_sep[0]].add(code_sep[1])
        code_2 = code.split(';')[1]
        code_sep = code_2.split()
        code_outgroup = code_sep[0]
        postcode_outgroups[code_outgroup] +=1
        postcodes[code_sep[0]].add(code_sep[1])
        return


def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


# audits postcodes
# counts outgroup occurances, and builds set of ingroups for each outgroup
def audit(osmfile):
    osm_file = open(osmfile, "r")
    postcodes = defaultdict(set)
    postcode_outgroups = defaultdict(int)
    n=0
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        n+=1
        #if n>200000: break
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter('tag'):
                if is_postcode(tag):
                    audit_postcode(postcode_outgroups,postcodes, tag.attrib['v'])
    osm_file.close()
    return postcode_outgroups, postcodes



if __name__ == '__main__':

    postcode_outgroups, postcodes = audit(OSM_FILE)


    print len(postcode_outgroups),'postcode outgroups in data (with counts of occurance) \n'
    pprint.pprint(sorted(postcode_outgroups.items()))

    # to print out the full 'sets' of ingroups for each outgroup, uncomment line below
    #pprint.pprint(sorted(postcodes.items()))
