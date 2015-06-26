# -*- coding: utf-8 -*-
"""
Created on Tue May 19 03:00:12 2015

AUTHOR
Erwin van den Berg
Based on code from Bart Vredebregt <bart.vredebregt@gmail.com>
"""
import os
import re
import time
import urllib
import urllib2
import xml.etree.ElementTree as ET
import requests

#################### Arguments:
# Downloada from all fields of law? Possible answers: True/False
download_from_all_fields_of_law = False

# the field of law, look here http://data.rechtspraak.nl/Waardelijst/Rechtsgebieden
field_of_law = 'http://psi.rechtspraak.nl/rechtsgebied#bestuursrecht_vreemdelingenrecht'

# maximum number of case laws that will be downloades as integer in a string
# maximum tested up to 15000
maximum_number_of_case_laws = '100'

# sorting the articles 
# 'DESC' for newest first or 'ASC' for oldest first
sorting = 'DESC'

# download the case laws to this folder
# path is in the folder of this script
save_case_laws_here = 'caselaws'


#################### Actual code:
def main(parameters):    
    # Start global timer
    start_time = time.time()
    
    # Fetch the list of ECLI's corresponding to the parameters
    eclis = get_eclis(parameters)

    # If the list of ECLI's is not empty, prepare for parsing
    if len(eclis) > 0:
        parse(eclis)
    else:
         print 'No eclis found. Try to change the parameters'
    
    print("Completed everything in {:.2f} seconds".format((time.time() - start_time)))
    


def parse(eclis):
    # Start function timer
    stage_start_time = time.time()
    
    folder_name = save_case_laws_here + '/'
    
    # check whether the directory exists and if not, make the folder
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)


        
  # Check whether there are any ECLIs in the shared todolist (eclis)
    while len(eclis) > 0:
                
        # Take and remove an ecli from the top of the shared todolist
        e = eclis.pop()

        # Fetch the file for the ecli popped before
        ecliFile = get_ecli_file_raw(e.text)
        
        # If the get_ecli_file function return None a time out has occurred
        if ecliFile is None:  # Time out has occurred

            # Put the ECLI back into the todolist
            eclis.append(e)

            # And start the loop again
            continue
                
        #file = os.path.normpath(folder_name + re.sub(":", "-", e.text) + '.xml')
        file = os.path.normpath(folder_name + re.sub(":", "-", e.text) + '.xml')
        
        #Write the XML to the file
        with open(file, "wb") as myfile:
            
            myfile.write(ecliFile)
    
    print("Completed saving ECLIs in {:.2f} seconds".format((time.time() - stage_start_time)))

            
# Get list of all wanted eclis
def get_eclis(parameters={'subject': 'http://psi.rechtspraak.nl/rechtsgebied#bestuursrecht_vreemdelingenrecht',
                          'max': '100', 'return': 'DOC'}):
    # Start function timer
    stage_start_time = time.time()

    # Print welcome message
    print("Loading ECLI data...".format())

    # URL encode the parameters
    encoded_parameters = urllib.urlencode(parameters)
    
    
    # Create an URL feed to the proper URL
    feed = urllib2.urlopen("http://data.rechtspraak.nl/uitspraken/zoeken?" + encoded_parameters)

    # print 'debug printing', ("http://data.rechtspraak.nl/uitspraken/zoeken?" + encoded_parameters)
    
    # Define Namespace for the XML file
    nameSpace = {'xmlns': 'http://www.w3.org/2005/Atom'}
        
    # Find all Entries in the results XML
    eclis = ET.parse(feed).findall("./xmlns:entry/xmlns:id", namespaces=nameSpace)

    # Print Completion message
    print("Completed loading ECLI data in {:.2f} seconds".format((time.time() - stage_start_time)))

    # Return the list of entry found above
    return eclis
    

# Get ecli file as it is on the web
def get_ecli_file_raw(ecli):
    # URL encode the parameters
    encoded_parameters = urllib.urlencode({'id': ecli})
    url = "http://data.rechtspraak.nl/uitspraken/content?" + encoded_parameters

    try:
        feed = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as err:    # This is the correct syntax
        print("{} timed out, retrying in 3 seconds!".format(ecli))
        print err
        # Sleep for 3 seconds to give the server time to restore
        time.sleep(3)

        # Pass the exception (proper error handling)
        pass

        # Return None to have the ECLI re-added to the todolist
        return None
    else:  # When no exception has occurred
    
        return feed.content

# Main function
if __name__ == '__main__':
    parameters = {}
                  
    if (not download_from_all_fields_of_law):
        parameters = {'subject': field_of_law, 'max': maximum_number_of_case_laws,
                      'return': 'DOC', 'sort': sorting}
    else:
        if download_from_all_fields_of_law:
            parameters = {'max': maximum_number_of_case_laws,
                          'return': 'DOC', 'sort': sorting}
           
    main(parameters)
    
