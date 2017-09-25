# open_street_map_project
A project completed for the Udacity Data Analysis Nanodegree programme to download, interrogate & clean data (on SW London) from the OSM project, 
then write it to an SQL database and runs a series of queries.


**OSM_project_submission.html**
The 'write up' of the project, including description of map area, cleaning issues, data investigation and additional ideas.

**swlondon_sample_submission.osm** a c. 10MB extract from the swlondon.osm file used in the project 

###### Python Scripts
**osm_sampling.py** 
A script to take a smaller sample from the large swlondon.osm file

**initial_street_name_audit.py** 
An initial audit of street names in the data, to see what street types are present

**element_type_count.py** 
Counts the different types of elements in the swlondon.osm file

**tag_type_review.py** 
Classifies tag types, and counts them. Options to print out the various tag type info as processing.

**street_name_audit.py** 
Audits street names , with mapping for proposed corrections

**k_attrib_audit.py**
Counts & outputs the data found  in tag 'k' attributes in the data

**postcode_audit.py**
Processes, audits & counts postcodes found in the data

**process_to_csv.py**
Processes swlondon.osm, makes all required cleaning changes (and prints those made) and writes output to csv files

**csv_to_database.py**
reads the created csv files, and writes all the content to the relevant tables in the database


