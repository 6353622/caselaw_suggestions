# -*- coding: utf-8 -*-
"""
AUTHOR
Erwin van den Berg
"""
import os
import re
import time
from collections import Counter

#################### Arguments:
# cutoff at which percentage of occurances in texts
# e.g. 
# document_freq_cutoff = 40 # means words are added to stop list if it appears in more than 40% of the texts
document_freq_cutoff = 15

# path to the folder that contains the case laws
# path is in the folder of this script
# case_laws_location = 'caselaws' # = standard folder name
case_laws_location = 'caselaws'


#################### Actual code:
def get_word_count(text_input):    
    words = re.findall(r'\w+', text_input)
    # Count how many times each word appears in doc
    word_counts_this_doc = Counter(words) 
    return word_counts_this_doc
    
    
def bool_doc_freq_above_treshold(term, treshold):
    above_treshold = False
    doc_freq = 0;
    for file in os.listdir(path):
        with open(path+file, "rt") as myfile:
            document_i = myfile.read()

        if term in document_i:
            doc_freq = doc_freq + 1
        
            # if doc_freq is above tresheld, take a shortcut, no need for more searching
            if doc_freq >= treshold:
                above_treshold = True
                break
   
    return above_treshold
    

def save_stopwords_to_file(stopwords_string):
    stage_start_time = time.time()
    #name of the folder
    stopwords_folder = 'stopwords/'
    # check whether the directory exists and if not, make the folder
    if not os.path.isdir(stopwords_folder):
        os.makedirs(stopwords_folder)

    #file = os.path.normpath(folder_name + re.sub(":", "-", e.text) + '.xml')
    file = os.path.normpath(stopwords_folder + 'stopwords.txt')
    
    #Write the stopwords to the file
    with open(file, "wb") as myfile:
        myfile.write(stopwords_string)
    
    print("Completed writing the stopwords to file in {:.2f} seconds".format((time.time() - stage_start_time)))
        
    



################## MAIN

# start timers
start_time = time.time()        
stage_start_time = time.time()
#path = fix_file_path(path)

path = case_laws_location + '/'

# check whether the directory exists
if not os.path.isdir(path):
    # if path does not exist, give the user feedback
    print 'path does not exist'

else:
    
    #create instance of total_word_counts
    total_word_counts = get_word_count('hoi')
    
    # counter for debugging
    countfiles = 0
    
    for file in os.listdir(path):
         # counter for debugging
        countfiles = countfiles+1

        with open(path+file, "rt") as myfile:
            text = myfile.read()
        
        # get word count
        word_count = get_word_count(text)
        
        # Count how many times each word appears in all docs
        total_word_counts = total_word_counts + word_count
        
        # debug switch
        if True:
            if not countfiles % 1000:
                print(countfiles , " docs processed (counting words) in {:.2f} seconds".format((time.time() - start_time)))

    print("Completed counting all words in corpus in {:.2f} seconds".format((time.time() - stage_start_time)))   
    print(len(total_word_counts), " words found in corpus")
    
    

    
    
    
    
    
    
    
    ############################# Create stop list file
    
    
    
    # stop words list 
    stopwordslist = []
    
    # Converts from counter to list
    word_count_list = total_word_counts.most_common()
    
    #print total_word_counts
    #print word_count_list
    
    document_freq_treshold = (document_freq_cutoff * countfiles )/100
    #print countfiles
    print (' document_freq_treshold  ') 
    print document_freq_treshold
    
    all_numbers = re.compile('\d')
    
    # counter just for debugging
    count_words_i = 0
    
    # start stage timer
    stage_start_time = time.time()
    
    for word in word_count_list:
        # counter just for debugging
        count_words_i = count_words_i +1
        
        # if the total word freq is les than the needed doc freq
        if (word[1] < document_freq_treshold):
            # break the loop
            break
        else:
            # continue if the word does not contain a number
            if not all_numbers.search(word[0]):
    
                if bool_doc_freq_above_treshold(word[0], document_freq_treshold):
                    stopwordslist.append(word[0])
                    
        # debug switch
        if True:
            if not count_words_i % 10:
                print(countfiles , " words processed (calc doc freq) in {:.2f} seconds".format((time.time() - stage_start_time)))
              
    print("Completed finding words above document freq treshold in {:.2f} seconds".format((time.time() - stage_start_time)))
            
   # print 'stopwordslist'
    #print stopwordslist
    
    # convert list to string
    stopwords_string = ' '.join(stopwordslist)
    #print stopwords_string
    
    # save string to file
    save_stopwords_to_file(stopwords_string)

    print("Completed everything in {:.2f} seconds".format((time.time() - start_time)))
