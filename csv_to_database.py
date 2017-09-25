
from collections import defaultdict
import re
import pprint
import csv
import codecs

import time

import sqlite3

###########################################################################
# CODE to create database, drop tables and create schema as required for osm data
###########################################################################

conn = sqlite3.connect('swlondon.sqlite')
cur = conn.cursor()

# Drop any existing tables
cur.execute('''DROP TABLE IF EXISTS nodes''')
cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
cur.execute('''DROP TABLE IF EXISTS ways''')
cur.execute('''DROP TABLE IF EXISTS ways_tags''')
cur.execute('''DROP TABLE IF EXISTS ways_nodes''')


# Create tables:
cur.execute('''
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
    );
''')

cur.execute('''
CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
    );
''')

cur.execute('''
CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
    );
''')

cur.execute('''
CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);
''')

cur.execute('''
CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);
''')


conn.commit()


#####################################################
# Opens csv files and reads data to list in memory
#####################################################

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

def parse_csv(datafile):
    data=[]
    n=0
    with open(datafile, 'r') as sd:
        r = csv.DictReader(sd)
        for line in r:
            data.append(line)
        return data

nodes_data = parse_csv(NODES_PATH)
nodes_tags_data = parse_csv(NODE_TAGS_PATH)
ways_data = parse_csv(WAYS_PATH)
ways_nodes_data = parse_csv(WAY_NODES_PATH)
ways_tags_data = parse_csv(WAY_TAGS_PATH)



#######################################################
# Functions for writing line from each list (from csv files) into relevant tables
#######################################################

def write_node_line (data):
    cur.execute(
        '''
    INSERT into nodes (id, lat, lon, user, uid, version, changeset, timestamp)
    VALUES (?,?,?,?,?,?,?,?)
        ''',
    (data['id'].decode('utf-8'), data['lat'].decode('utf-8'), data['lon'].decode('utf-8'),
     data['user'].decode('utf-8'), data['uid'].decode('utf-8'),
     data['version'].decode('utf-8'), data['changeset'].decode('utf-8'),
     data['timestamp'].decode('utf-8'))
    )

def write_node_tags_line (data):
    cur.execute(
        '''
    INSERT into nodes_tags (id, key, value, type)
    VALUES (?,?,?,?)
        ''',
    (data['id'].decode('utf-8'), data['key'].decode('utf-8'),
     data['value'].decode('utf-8'), data['type'].decode('utf-8'))
    )


def write_ways_line (data):
    cur.execute(
        '''
    INSERT into ways (id, user, uid, version, changeset, timestamp)
    VALUES (?,?,?,?,?,?)
        ''',
    (data['id'].decode('utf-8'), data['user'].decode('utf-8'), data['uid'].decode('utf-8'),
     data['version'].decode('utf-8'),
      data['changeset'].decode('utf-8'), data['timestamp'].decode('utf-8'))
    )


def write_ways_tags_line (data):
    cur.execute(
        '''
    INSERT into ways_tags (id, key, value, type)
    VALUES (?,?,?,?)
        ''',
    (data['id'].decode('utf-8'), data['key'].decode('utf-8'),
     data['value'].decode('utf-8'), data['type'].decode('utf-8'))
    )

def write_ways_nodes_line (data):
    cur.execute(
        '''
    INSERT into ways_nodes (id, node_id, position)
    VALUES (?,?,?)
        ''',
    (data['id'].decode('utf-8'), data['node_id'].decode('utf-8'),
     data['position'].decode('utf-8'))
    )

# list of the data dicts and read functions to write their data to SQL tables
DATA_DICTS = [nodes_data, nodes_tags_data, ways_data, ways_nodes_data, ways_tags_data]
READ_FNS = [write_node_line, write_node_tags_line, write_ways_line, write_ways_nodes_line, write_ways_tags_line]

# MAIN function
# loops through data dicts in parallel with associate SQL line writing function
# writes each line of data dict to the relevant SQL table

for data, function in zip(DATA_DICTS,READ_FNS):
    n=0
    for line in data:
        n+=1
        if n%10000==0:
            conn.commit()
        function(line)


conn.commit()
print 'DONE!'
