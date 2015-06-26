# -*- coding: utf-8 -*-
"""
Created on Sun May 17 16:54:41 2015

AUTHOR
Erwin van den Berg
"""
import operator
import os
import re
import time

#################### Arguments:
# path to the folder that contains the case laws
# path is in the folder of this script
# case_laws_location = 'caselaws' # = standard folder name
case_laws_location = 'caselaws'

# delete the smallest X percentage files from the corpus
# percentage = 1 # = standard percentage
smallest_doc_percentage = 1


#################### Actual code:
def filter_smallest_files(folder_name, percentage):
    # start timer
    stage_start_time = time.time()
    
    # check if path+irrelevant/ exists
    smallest_folder = 'smallest_' + str(percentage) + '_percent/'
    
    filtered_texts = 0
    
    # check whether the directory exists and if not, make the folder
    if not os.path.isdir(smallest_folder):
        os.makedirs(smallest_folder)
    
    # get all files in folder
    getall = [ [file, os.path.getsize(folder_name+file)] for file in os.listdir(folder_name) if file.endswith(".txt") ]
    
    # smallest files on top of list    
    sorted_ascending_size = sorted(getall, key=operator.itemgetter(1))
    
    # amount of files that will be moved
    amount_of_files = int(len(sorted_ascending_size) * (0.01 * percentage))
    
    # For the calculated number of files
    for x in range(0, amount_of_files):
        
        # print "We're on time %d" % (x)    
        file = sorted_ascending_size[x][0]
        # rename the file extension from .xml to .irr so it will be excluded
        base_file, ext = os.path.splitext(file)
        # rename the extension of these files to .irr and move them in subfolder 'irrelevant' 
        #os.rename(path+base_file+ext, (path + base_file + '.irr') )
        os.rename(folder_name+base_file+ext, (smallest_folder + base_file + '.small') )
        # counter plus one
        filtered_texts += 1
        


    # Print Completion message
    print("Completed filtering the smallest case laws {:.2f} seconds".format((time.time() - stage_start_time)))


# filter out the files that don't contain the relevant word (query)
def filter_irrelevant_texts(path, query):
    # start timer
    stage_start_time = time.time()
    
    # folder name for irrelevant texts
    irrelevant = 'irrelevant/'
        
    # check whether the directory exists
    if not os.path.isdir(irrelevant):
        os.makedirs(irrelevant)

    query = query.lower()    
    filtered_texts = 0
    
    for file in os.listdir(path):
        if file.endswith(".xml"):
        
            f = open(path + file, 'rt')
            txt = f.read()
            f.close()

            count = len( re.findall( query, txt.lower() ) )
            
            # if word is not found
            if count == 0:
                # rename the file extension from .xml to .irr so it will be excluded
                base_file, ext = os.path.splitext(file)
                # rename the extension of these files to .irr and move them in subfolder 'irrelevant' 
                #os.rename(path+base_file+ext, (path + base_file + '.irr') )
                os.rename(path+base_file+ext, (irrelevant + base_file + '.irr') )
                # counter plus one
                filtered_texts += 1
                
    # Print Completion message
    print("Completed filtering irrelevant case laws {:.2f} seconds".format((time.time() - stage_start_time)))

    return filtered_texts
    
    
# delete irrelevant parts (procesverloop and beslissing) out of the files
# also delete all xml code, and rename the .xml extension to .txt
def delete_irrelevant_parts(path):
    # start timer
    stage_start_time = time.time()
    
    # initialize
    remove_before = '<inhoudsindicatie id='
    split_file_at = '</inhoudsindicatie>'
    part_b_remove_before = 'overwegingen<'
    part_b_remove_before_alt = 'overwegingen'
    part_b_remove_after = 'beslissing'
    
    text_part_a = ''
    text_part_b = ''
    
    for file in os.listdir(path):
        if file.endswith(".xml"):            
            
            with open(path+file, "rt") as myfile:
                text = myfile.read()
            
            # make text lowercase
            text = text.lower()
            #print text
            splitted = text.split(remove_before, 1)
            if len(splitted) == 1:
                # change nothing, since text stays the same
                text = text
            if len(splitted) == 2:
                text = remove_before+splitted[1]
                
            # Split text in two parts, part a is done, and part b needs more preprocessing
            splitted = text.split(split_file_at, 1)
            # if not found, just make the whole text part B
            if len(splitted) == 1:
                text_part_a = ''
                text_part_b = text
            if len(splitted) == 2:
                text_part_a = splitted[0]+split_file_at
                text_part_b = splitted[1]
        
        
            # Remove text before overwegingen (remove processverloop)
            splitted = text_part_b.split(part_b_remove_before, 1)
            # if 'overwegingen<' is not found (only in small percentage of the tested corpus) search for 'overwegingen'
            if len(splitted) == 1:
                splitted_alt = text_part_b.split(part_b_remove_before_alt, 1)
                if len(splitted_alt) == 1:
                    # change nothing, since text stays the same
                    text_part_b = text_part_b
                if len(splitted_alt) == 2:
                    text_part_b = part_b_remove_before_alt+splitted_alt[1]
            if len(splitted) == 2:
                text_part_b = part_b_remove_before+splitted[1]
            
            
            
            # if beslissing is part of the text
            if part_b_remove_after in text_part_b:
                # Remove text after last occurrence of beslissing
                splitted = text_part_b.rsplit(part_b_remove_after,1)
                if len(splitted) == 2:
                    text_part_b = splitted[0]
                
                
            # Remove the xml code between < and > and remove excess white space
            text_part_a = fix_format(text_part_a)
            text_part_b = fix_format(text_part_b)
            
            # combine both parts of the text again
            text = text_part_a + '\n\n' + text_part_b
            
            with open(path+file, "wt") as myfile:
                myfile.write(text)
    
            # The file no longer have XML format, so change file extension to .txt
            base_file, ext = os.path.splitext(file)
            # rename the extension of these files to .irr and move them in subfolder 'irrelevant'
            os.rename(path+base_file+ext, (path + base_file + '.txt') )
            
    # Print Completion message
    print("Completed deleting irrelevant parts in {:.2f} seconds".format((time.time() - stage_start_time)))
            
        
# remove xml code and remove excess whitespace
def fix_format(text):
    # remove xml code, by removing everything between < and >
    text = re.sub('<[^>]+>', ' ', text)
    
    #remove excess whitespace
    text = ' '.join(text.split())   

    return text

# Start the main proces for the preprocessing of case laws
if __name__ == '__main__':
    # start timer
    start_time = time.time()     
    
    folder_name = case_laws_location + '/'
    
    # check whether the directory exists
    if not os.path.isdir(folder_name):
        # if path does not exist, give the user feedback
        print 'path does not exist'


    # if folder exist, start the preprocessing                
    else:          
        # Filter the texts that don't contain "overwegingen"
        relevant_word = 'overwegingen'
        filter_results = filter_irrelevant_texts(folder_name, relevant_word)
        print filter_results, 'texts filtered because they are missing "', relevant_word, '"'
            
        # Filter the texts that don't contain "inhoudsindicatie"
        relevant_word2 = 'inhoudsindicatie'
        filter_results2 = filter_irrelevant_texts(folder_name, relevant_word2)
        print filter_results2, 'texts filtered because they are missing "', relevant_word2, '"'
        
        # Delete irrelevant parts of the case files (procesverloop and beslissing)
        # delete xml code and change extension of the files to .txt
        delete_irrelevant_parts(folder_name)
        
        # delete the smallest 1 % of the files
        filter_smallest_files(folder_name, smallest_doc_percentage)
        

    	# Print Completion message
    print("Completed everything in {:.2f} seconds".format((time.time() - start_time))) 
