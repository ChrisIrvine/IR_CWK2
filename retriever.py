#!/usr/bin/python3
# needs improving to remove forced type conversions

import sys
import math
import re
import json
import csv
import operator
import numpy as plt
import matplotlib.pyplot as plt
import copy


# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []
doclength = {}
doctitles = {}
docheaders = {}
results = {}

def main():
    # code for testing offline
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]
    answer = []

    read_index_files()

    #answer = retrieve_bool(query_terms)
    answer = retrieve_vector(query_terms)

    write_result_files()

    print('Query: ', query_terms)
    i = 0
    for docid in answer:
        i += 1
        print(i, docids[docid])    

def read_index_files():
    ## reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclength
    global doctitles
    global docheaders
    # open the files
    in_d = open('docids.txt', 'r')
    in_v = open('vocab.txt', 'r')
    in_p = open('postings.txt', 'r')
    in_dl = open('doclength.txt', 'r')
    # load the data
    docids = json.load(in_d)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    doclength = json.load(in_dl)
    with open('doctitles.csv', newline='') as titles:
        reader = csv.DictReader(titles)
        for row in reader:
            for key, val in row.items():
                doctitles[key] = val
    with open('docheaders.csv', newline='') as headers:
        reader = csv.DictReader(headers)
        for row in reader:
            for key, val in row.items():
                doctitles[key] = val
    # close the files
    in_d.close()
    in_v.close()
    in_p.close()
    in_dl.close()

    return

def write_result_files():
    # declare refs to global variables
    global results

    w = csv.writer(open("results.csv", "w"))
    
    for key,val in enumerate(results):
        w.writerow([key, val])

    return

def clean_query(query_terms):
    # No Numbers
    cleantext = re.sub('(\d)', '', query_terms)
    # No Abbreviations
    cleantext = re.sub('(n\'t\b)', ' not', cleantext)
    cleantext = re.sub('(\'ll\b)', ' will', cleantext)
    cleantext = re.sub('(I\'m)', 'I am', cleantext)
    cleantext = re.sub('(I\'ve)', 'I have', cleantext)
    cleantext = re.sub('(\w*\'\w*)', '', cleantext)
    # No Punctuation
    cleantext = re.sub('([\W]+)', ' ', cleantext)
    return cleantext

# def retrieve_bool(query_terms):
#     ## a function to perform Boolean retrieval with ANDed terms
#     answer = []
#     operator = ''
#     #### your code starts here ####
#     for plist in postings.get(vocab.index(query_terms[0])):
#         for post in plist:
#             answer.append(post)

#     for term in query_terms:
#         if term in ('AND', 'OR', 'NOT'):
#             operator = term
#             continue
#         try:
#             termid = vocab.index(term)
#         except:
#             print('Not found: ', term, ' is not in vocabulary')
#             continue

#         if operator == 'OR':
#             for plist in postings.get(termid):
#                 for post in plist:
#                     answer.append(post)
#             answer = sorted(list(set(answer)))
#             operator = ''

#         elif operator == 'AND':
#             merge_list = answer[:]
#             answer = []
#             for plist in postings.get(termid):
#                 for post in plist:
#                     print('post = ', post)
#                     if post in merge_list:
#                         answer.append(post)
#             answer = sorted(list(set(answer)))
#             merge_list = []
#             operator = ''

#         elif operator == 'NOT':
#             for plist in postings.get(termid):
#                 for post in plist:
#                     if post in answer:
#                         answer.remove(post)
#             operator = ''
#     #### your code ends here ####
#     return answer

def retrieve_vector(query_terms):
    global docids
    global vocab
    global postings
    global docheaders
    global doctitles
    global results

    answer = []
    idf = {}
    collection = 0
    scores = {}
    query_vector = []
    query_set = set(query_terms)
    new_results = {}

    for term in query_set:
        try:
            termid = vocab.index(term.lower())
        except:
            print('Not found: ', term, ' is not in vocabulary')
            continue
        for post in postings.get(str(termid)):
            collection += 1

        idf[termid] = (1+math.log(len(postings.get(str(termid)))))/(collection)

        print(idf[termid])
        for doc, titleWords in enumerate(doctitles):
            if term in titleWords:
                idf[termid] = float(idf.get(termid)) * float(2.5)
    
        for doc, headerWords in enumerate(docheaders):
            if term in headerWords:
                idf[termid] = float(idf.get(termid)) * float(1.5)
        #print('retrieve_vector: term = ', term, 'termid = ', termid, 'idf = ', idf[termid])

    i = -1
    for termid in sorted(idf, key=idf.get, reverse=True):
        i += 1
        query_vector.append(idf[termid]/len(query_set))

        for post in postings.get(str(termid)):
            #print ('post[0] = ', post[0], ' post[1] = ', post[1], ' idf = ', idf.get(termid), ' doclength = ', doclength.get(post[0]))
            if post[0] in scores:
                scores[post[0]] += (idf.get(termid) * float(post[1])) / float(doclength.get(str(post[0]))) * query_vector[i]
            else:
                scores[post[0]] = (idf.get(termid) * float(post[1])) / float(doclength.get(str(post[0]))) * query_vector[i]
            #print((idf.get(termid) * post[1]) / doclength.get(post[0]))

    for docid in sorted(scores, key=scores.get, reverse=True):
        results[docids[int(docid)]] = {scores.get(docid)}

    results = sorted(results.items(), key=operator.itemgetter(1))

    i = 0
    for key in results:
        i += 1
        answer.append(docids.index(str(key[0])))
        new_results[key[0]] = key[1]
        if i != 10:
            continue
        else:
            break
    
    results = new_results

    return answer

# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
