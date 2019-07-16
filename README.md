# link_checker
Python script to find erroneous links in bib record
This link checker was inspired by <a href="https://github.com/pulcams/elink_checker">elink_checker</a> by Princeton University Library's Cataloging Archival and Metadata Services (CAMS).

# What you need
1. Python (3)
2. cx_Oracle (for generate_input_file.py)
3. sqlite3 (for check_status.py)

## generate_input_file.py
This script generates an input csv file that contains bib record ids, URL hosts, URLs, and holding location code per library department or collection. If it contains more than 10,000 rows, it is split by 10,000 rows. 
Make sure to replace “ENTER_XXX” with your own value in the script.

## check_status.py
This script checks HTTP status of each link in the input file and generates an output csv file. Once the process is done, it automatically sends an output file to appropriate department or collection staff so that they can review the file and correct or delete links. All data is saved in a sqlite database.
Make sure to replace “ENTER_XXX” with your own value in the script.
