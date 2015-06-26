# -*- coding: utf-8 -*-
"""
AUTHORS
The calculation of the most similar topic mixtures and giving suggestions is done by:
Erwin van den Berg

The formatting of the mallet composition file is done by: 
DARIAH-DE
And is taken from here:
https://de.dariah.eu/tatom/topic_model_mallet.html
Which is published under a Creative Commons Attribution 4.0 International license (CC-BY 4.0):
https://creativecommons.org/licenses/by/4.0/
"""
# Tested with python 3.4
import numpy as np
import itertools
import operator
import re
import time

#################### Arguments:
# The ECLI name of which you want to find the suggestions
# Use all caps in the name, and use no file extension
# Examples
# ECLI_name = 'ECLI:NL:RBSGR:2009:BH7787'
# ECLI_name = 'all' # to give back similarities for all ECLIs, WARNING THIS COULD TAKE LONG
# ECLI_name = 'multi' # to give back similarities for multiple ECLIs, WARNING NEED TO SPECIFY ECLI_multi
#ECLI_name = 'ECLI:NL:RBDHA:2014:3327'
ECLI_name = 'ECLI:NL:RBSGR:2009:BH7787'

# ECLI_multi is only needed when ECLI_name is set to 'multi'
# Example:
# ECLI_multi =['ECLI:NL:RBSGR:2009:BH7787','ECLI:NL:RBSGR:2009:BK7528'];
ECLI_multi =['ECLI:NL:RBSGR:2009:BH7787','ECLI:NL:RBSGR:2009:BK7528','ECLI:NL:RBSGR:2012:BX3443','ECLI:NL:RBZWB:2013:3140','ECLI:NL:RVS:2011:BQ8488','ECLI:NL:RVS:2012:BV1584','ECLI:NL:RVS:2012:BY7272','ECLI:NL:RVS:2012:BY7391','ECLI:NL:RVS:2013:2315','ECLI:NL:RVS:2013:2616','ECLI:NL:RVS:2014:1575'];

# The number of suggestions you want (best suggestion first)
# Zero gives all ECLIs as suggestions (best suggestion first
# Example:
# number_of_suggestions = 0
number_of_suggestions = 3

# filepath of the MALLET compposition file
# Example:
# filepath = 'C:/mallet/step4/composition.txt'
filepath = 'C:/mallet/step4/composition.txt'


#################### Actual code:
doctopic_triples = []
mallet_docnames = []

# from som of error to simililarity
def sum_of_error_to_similarity(sum):
    # sum of error ranges from 0 to 2
    # therefore, similarity is ((2-sum)/2)*100 = (2-sum)*50
    similarity = (2-sum)*50
    return similarity
    
#For 1 ECLI get pairs with differences
def get_list_of_suggestions(base_number, number_of_suggestions):
    suggestion_list = []
    
    # first element of the suggestion list is the ECLI name
    suggestion_list.append((100, mallet_docnames[base_number]))
    #just checking if it is the same size
    if len(mallet_docnames)  == len(doctopic):
        doc1 = doctopic[base_number]
        #calculate most similar by minimizing the square errors
        counter = -1;
        # print (count1)
        for doc2 in doctopic:
            counter += 1
            #print (counter)
            #print ("start")
            
            # if the two documents are not the same
            if not np.array_equal(doc1, doc2):
                # then calculate the sum of squered errors
                errorsum  = sum_of_squared_errors(doc1,doc2)
                # or use sum of absolute errors
                #errorsum  = sum_of_absolute_errors(doc1,doc2)
                similarity = sum_of_error_to_similarity(errorsum)
                
                # add suggestion to list
                suggestion_list.append((similarity, mallet_docnames[counter]))
        
    # Sort suggestions from most similar to least similar mixture
    suggestion_list = sorted(suggestion_list,  key=operator.itemgetter(0), reverse=True)
    
    # if the amount of suggestions is not specified (0), print all
    # if the amount of suggestions is specified (>0), give back this amount
    if number_of_suggestions > 0:
        # Give back the predifined number of suggestions (+1 because first element is base doc)
        suggestion_list = suggestion_list[:number_of_suggestions+1]  
    return suggestion_list
    
def fix_file_path(path):
    path = path.replace('/', '\\')
    return path

def sum_of_squared_errors(vector1, vector2):
    difference = vector1-vector2
    sum = np.dot(difference, difference)
    return sum
     
def sum_of_squared_errors2(vector1, vector2):
    difference = vector1-vector2
    sum = (difference**2).sum(dtype='float')
    return sum 

def sum_of_absolute_errors(vector1, vector2):
    difference = vector1-vector2
    sum = (np.absolute(difference)).sum(dtype='float')
    return sum 
    
def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    args =  [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
        

def rename_full_file_path_to_file_name(file_name):
    remove_before = '/'
    remove_extension = '.txt'
    
    # if / is in file_name, remove everything before last /
    if remove_before in file_name:
        # Only keep file_name after last occurrence of beslissing
        splitted = file_name.rsplit(remove_before,1)
        if len(splitted) == 2:
            file_name = (splitted[1])
            
    if remove_extension in file_name:
        splitted = file_name.rsplit(remove_extension,1)
        if len(splitted) == 2:
            file_name = splitted[0]
            
    return file_name



# Main
# Start global timer
start_time = time.time()

# Start Timer for this stage
stage_start_time = time.time() 

filepath = fix_file_path(filepath)
    
with open(filepath) as f:
    f.readline()  # read one line in order to skip the header
    for line in f:
        docnum, docname, *values = line.rstrip().split('\t')
        
        # rename the full file path to only the name of the file (without extension)        
        docname = rename_full_file_path_to_file_name(docname)
        # rename the '-' in the ECLI name back to ':'
        docname = re.sub("-", ":", docname) 
        
        mallet_docnames.append(docname)
        for topic, share in grouper(2, values):
            triple = (docname, int(topic), float(share))
            doctopic_triples.append(triple)

# sort the triples
# triple is (docname, topicnum, share) so sort(key=operator.itemgetter(0,1))
# sorts on (docname, topicnum) which is what we want
doctopic_triples = sorted(doctopic_triples, key=operator.itemgetter(0,1))

# sort the document names rather than relying on MALLET's ordering
mallet_docnames = sorted(mallet_docnames)

# collect into a document-term matrix
num_docs = len(mallet_docnames)

num_topics = len(doctopic_triples) // len(mallet_docnames)

# the following works because we know that the triples are in sequential order
doctopic = np.zeros((num_docs, num_topics))

# doctopic is an matrix with dimensions: numd_ocs * num_topics
# sorted based on docname all elements in array are sorted topic share

for triple in doctopic_triples:
    docname, topic, share = triple
    row_num = mallet_docnames.index(docname)
    doctopic[row_num, topic] = share

# Print Completion message
print("Completed sorting the matrices of mixtures for all ECLIs in {:.2f} seconds".format((time.time() - stage_start_time)))

    
    
    
    
# Calculation most similar ECLI based on mixture    
############################################################################################################
    
# Start function timer
stage_start_time = time.time()    

# check whether number_of_suggestions is specified
if not isinstance(number_of_suggestions, int):
    # when number_of_suggestions is not specified, demonstrate this program with five suggestions
    print ('no amount of suggestions specified, so I will demonstrate 5 suggestions')
    number_of_suggestions = 5

# check if ECLI_name is specified
if (not ECLI_name) or (not isinstance(ECLI_name, str)):
    # when no ECLI is specified,  demonstrate this program with one ECLI
    ECLI_name = mallet_docnames[1]
    print ('no ECLI specified, so I will demonstrate using ECLI:')
    print (ECLI_name)

# change '-' to ':'
ECLI_name = re.sub("-", ":", ECLI_name) 
# if ECLI_name is in mallet_docnames
if ECLI_name in mallet_docnames:
    # calc similarity for just one ECLI
    # give the index for this file
    ECLI_index = mallet_docnames.index(ECLI_name)
    suggestions_for_ECLI = get_list_of_suggestions(ECLI_index, number_of_suggestions)
    print (suggestions_for_ECLI)
    
else:    
    # if ECLI_name is 'all'
    if ECLI_name.lower() == 'multi':
        # List that will contain suggestions for all ECLIs
        suggestions_for_multi_ECLIs = []
        # calculate all similarities for all ECLIs
        print ('Now calculating all similarities for multiple ECLIs')
        print ('This can take a while')
        
        for ECLI_name in ECLI_multi:
                ECLI_index = mallet_docnames.index(ECLI_name)
                suggestions_for_ECLI = get_list_of_suggestions(ECLI_index, number_of_suggestions)
                suggestions_for_multi_ECLIs.append(suggestions_for_ECLI)
        # print the suggestions for all ECLIs
        print (suggestions_for_multi_ECLIs)
    # if ECLI_name is not in mallet_docnames, give user feedback
        
        
    else:
        # if ECLI_name is 'all'
        if ECLI_name.lower() == 'all':
            # List that will contain suggestions for all ECLIs
            suggestions_for_all_ECLIs = []
            # calculate all similarities for all ECLIs
            print ('Now calculating all similarities for all ECLIs')
            print ('This can take a while')
            for ECLI_index_i in range(0, len(mallet_docnames)):
                suggestions_for_ECLI_i = get_list_of_suggestions(ECLI_index_i, number_of_suggestions)
                suggestions_for_all_ECLIs.append(suggestions_for_ECLI_i)
            # print the suggestions for all ECLIs
            print (suggestions_for_all_ECLIs)
        # if ECLI_name is not in mallet_docnames, give user feedback        
        else:
            print ('Cant find supplied ECLI. Use one from this list:')
            print (mallet_docnames)
            

# Print Completion message
print('\n')
print("Completed calculating most similar ECLI's in {:.2f} seconds".format((time.time() - stage_start_time)))# Print Completion message
print("Completed everything in {:.2f} seconds".format((time.time() - start_time)))
