#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Generate a list of URLs per department/collection location
# Reference: https://www.programcreek.com/python/example/94405/cx_Oracle.makedsn

import cx_Oracle
import csv
import datetime

#===============================================================================
# defs
#===============================================================================

def split(filehandler):
# Split csv into separate files containing 10,000 rows
    csvfile = open(filehandler, 'r').readlines()
    filename = 1
    output_name = str(filehandler)[:-4] + '_'
    for i in range(len(csvfile)):
        if i % 10000 == 0:
            open(output_name + str(filename) + '.csv', 'w+').writelines(csvfile[i:i+10000])
            filename += 1

#===============================================================================
# variables
#===============================================================================

# List of reporting departments
# For example, unit_list = ['ART', 'DIV']
unit_list = ['''ENTER_LIST_OF_DEPTS''']

# Query
query = {'''ENTER_SQL'''}
'''
For example
query = {
'ART':"""                    
    SELECT * FROM (                
    SELECT
     bib_master.bib_id,
     elink_index.url_host,
     elink_index.link,
     location.location_code,
     ROW_NUMBER() OVER (PARTITION BY bib_master.bib_id, elink_index.link ORDER BY bib_master.bib_id) RowNumber
    FROM
     elink_index
     INNER JOIN bib_master ON elink_index.record_id = bib_master.bib_id
     INNER JOIN bib_mfhd ON bib_master.bib_id = bib_mfhd.bib_id
     INNER JOIN mfhd_master ON bib_mfhd.mfhd_id = mfhd_master.mfhd_id
     INNER JOIN location ON mfhd_master.location_id = location.location_id
    WHERE
     bib_master.suppress_in_opac = 'N'
     AND elink_index.record_type = 'B'
     AND mfhd_master.suppress_in_opac = 'N'
     AND mfhd_master.display_call_no NOT LIKE '%UNCAT%'
     AND mfhd_master.display_call_no NOT LIKE '%On Order%'
     AND mfhd_master.display_call_no NOT LIKE '%In Process%'
     AND location.location_id IN (
         '1',
         '2',
         '3'
     )) a
     WHERE RowNumber = 1
    """,
'DIV':"""                    
    SELECT * FROM (                
    SELECT
     bib_master.bib_id,
     elink_index.url_host,
     elink_index.link,
     location.location_code,
     ROW_NUMBER() OVER (PARTITION BY bib_master.bib_id, elink_index.link ORDER BY bib_master.bib_id) RowNumber
    FROM
     elink_index
     INNER JOIN bib_master ON elink_index.record_id = bib_master.bib_id
     INNER JOIN bib_mfhd ON bib_master.bib_id = bib_mfhd.bib_id
     INNER JOIN mfhd_master ON bib_mfhd.mfhd_id = mfhd_master.mfhd_id
     INNER JOIN location ON mfhd_master.location_id = location.location_id
    WHERE
     bib_master.suppress_in_opac = 'N'
     AND elink_index.record_type = 'B'
     AND mfhd_master.suppress_in_opac = 'N'
     AND mfhd_master.display_call_no NOT LIKE '%UNCAT%'
     AND mfhd_master.display_call_no NOT LIKE '%On Order%'
     AND mfhd_master.display_call_no NOT LIKE '%In Process%'
     AND location.location_id IN (
         '4',
         '5',
         '6'
     )) a
     WHERE RowNumber = 1
    """}
'''

#===============================================================================
# main
#===============================================================================

# Make connection to the oracle database
dsn = cx_Oracle.makedsn('''ENTER_HOST,ENTER_PORT,ENTER_DATABASE NAME''') # from tnsnames.ora
con = cx_Oracle.connect(user='''ENTER_USERNAME''',password='''ENTER_PASSWORD''',dsn=dsn)
cur = con.cursor()

# Select department/collection location
unit = '' 
while unit not in unit_list:
    unit = input ('Enter unit name: ')

# Execute query
cur.execute(query[unit])
r = cur.fetchall()
cur.close()
con.close()

now = datetime.datetime.now()

# Create output csv file
output_name = unit + '_' + now.strftime('%Y%m%d') + '.csv'

# Write query results to output csv file    
with open(output_name, 'w', newline='', encoding='utf-8-sig') as outfile:
    writer = csv.writer(outfile)
    c = 0
    for row in r:
        id = str(row[0])
        url = row[1]	
        host = row[2]
        loc = row[3]
        writer.writerow((id,url,host,loc))
        c += 1	
    print('links in ELINK_INDEX: ', c)
outfile.close()

# Split csv into separate files containing 10,000 rows
if c > 10000:
    split(output_name)