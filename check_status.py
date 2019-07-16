#! python3
# -*- coding: utf-8 -*-
# Check status of links within catalog records
import requests
import csv
import time
import sqlite3
import smtplib
from os.path import basename
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#===============================================================================
# defs
#===============================================================================
       
def check_url(u):
# Check url u. Return HTTP response.   
    try:
        r = requests.head(u, allow_redirects=True, timeout=50)
        code = r.status_code  
    except (requests.HTTPError, requests.URLRequired, requests.exceptions.RequestException, requests.TooManyRedirects, requests.ConnectionError, requests.ConnectTimeout, requests.ReadTimeout, requests.exceptions.Timeout):
        code = 'Error'
    if not str(code).startswith('2'):
        try:
            r = requests.get(u, allow_redirects=True, timeout=50)
            code = r.status_code           
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.exceptions.Timeout):
            code = 'Timeout Error'              
        except (requests.TooManyRedirects, requests.ConnectionError):
            code = 'Connection Error' 
        except (requests.HTTPError, requests.URLRequired, requests.exceptions.RequestException):
            code = 'Other Error'                    
    return code   
  
def send_email(attach_file, body, recipients, subject):
# Send email with file attachment. 
    sender = '''ENTER_EMAIL_ADDRESSES'''
    msg = MIMEMultipart()
    msg['from'] = sender
    msg['To'] = ','.join(recipients)
    msg['date'] = formatdate(localtime=True)
    msg['subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        file = attach_file
        part = MIMEBase('application', "octet-stream")
        with open(file, 'rb') as fh:
            part.set_payload(fh.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', \
                                          filename=basename(file))
            msg.attach(part)
    except (ValueError, TypeError):
        pass 
    smtp = smtplib.SMTP('''ENTER_HOST''')
    smtp.sendmail(sender, recipients, msg.as_string())
    smtp.close()     

#===============================================================================
# variables
#===============================================================================

# list of reporting departments
#For example, unit_list = ['ART', 'DIV']
unit_list = ['''ENTER_LIST_OF_DEPTS''']

# recipients' email addresses of each department
# For example, recipients = dict(ART=['abc@xxx.edu'], DIV=['abc@xxx.edu','def@xxx.edu'])
recipients = dict('''ENTER_EMAIL_ADDRESSES''')

#===============================================================================
# main
#===============================================================================

# Create and connect database
# For example, conn = sqlite3.connect('xxx.sqlite')
conn = sqlite3.connect('''ENTER_DATABASE''')


cur = conn.cursor()		

# Create table								
cur.executescript('''
CREATE TABLE IF NOT EXISTS Print (
    ID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    BibID  INTEGER,
    Host    TEXT,
    URL     TEXT,
	Status		TEXT,
    MFHD_Location   TEXT,
	Check_Date  DATE,
    Unit    TEXT
);
''')

# Record start time
start_time = time.time()

# Select input csv file and generate output csv file
input_name = input('Enter input name: ')
output_name = input_name[:-4] + "_output.csv"

# Select unit name to email
unit = '' 
while unit not in unit_list:
    unit = input('Select unit name: ')

# Email subject
subject = 'Link Errors (' + unit + ')' 

# Error counts    
not_found = connection_error = timeout_error = other_error = 0

# Open output csv file
with open(output_name, 'w', newline='', encoding='utf-8-sig') as csvoutput:
    csv_out = csv.writer(csvoutput, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
    csv_out.writerow(["ID","HOST","URL","STATUS","MFHD_LOC"])   
       
# Open input csv file 
    rows = csv.reader(open(input_name, 'r', encoding='utf-8-sig'))    
    num_lines = len(open(input_name).read().splitlines())
    count = 0
    
# List of unique urls   
    url_list = dict()

# Check each url
# If same link has not been checked yet, check its http status and update results to url_list
# If same link has already been checked, get result from url_list   
    for row in rows:
        bib = str(row[0])
        host = row[1]
        url = row[2]
        mfhd_loc = row[3]
        if url not in url_list:
            code = check_url(url)           
            url_list.update({url:code})        
        else:
            code = url_list.get(url)                   
        count += 1

# Write results to console       
        print (str(count) +  " of " + str(num_lines) + " | " + bib, code)

# Write error results to output csv file
        if str(code).startswith('400') or str(code).startswith('404'):
            csv_out.writerow([bib, host, url, code, mfhd_loc])
            not_found += 1
        if str(code).startswith('Connection'):
            csv_out.writerow([bib, host, url, code, mfhd_loc])
            connection_error += 1
        if str(code).startswith('Timeout'):
            csv_out.writerow([bib, host, url, code, mfhd_loc])
            timeout_error += 1 
        if str(code).startswith('Other'):
            csv_out.writerow([bib, host, url, code, mfhd_loc])
            other_error += 1             

# Write results to database                           
        cur.execute('SELECT ID FROM Print WHERE BibID = ? AND URL = ?', (bib, url, )) 
        fetch = cur.fetchone()
        if fetch is None:
            cur.execute('INSERT INTO Print (BibID, Host, URL, Status, MFHD_Location, Check_Date, Unit) VALUES ( ?, ?, ?, ?, ?, CURRENT_DATE, ? )', (bib, host, url, code, mfhd_loc, unit) )
        else: 
            cur.execute('UPDATE Print SET Status = ?, Check_Date = CURRENT_DATE, Unit = ? WHERE ID = ?', (code, unit, fetch[0],))
        conn.commit()       
csvoutput.close()
cur.close()

# If there is any error, email results
text_body = 'Among ' + str(num_lines) + ' links' + '\n\n400/404 Error = ' + str(not_found) + '\nConnection Error = ' + str(connection_error) + '\nTimeout Error = ' + str(timeout_error) + '\nOther Error = ' + str(other_error)
if not_found + connection_error + timeout_error + other_error > 0:        
    send_email(output_name, text_body, recipients[unit], subject)
print (text_body)
print("\n%f seconds" % (time.time() - start_time))