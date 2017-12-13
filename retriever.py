import sys
import math
import re
import json
import csv
import operator
import nltk
from nltk.corpus import wordnet

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []
doclength = {}
doctitles = {}
docheaders = {}
snippets = {}
results = {}

def main():
    # code for testing offline
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]

    #process query
    query_terms = clean_query(' '.join(query_terms))
    query_terms_list = [t.lower() for t in query_terms.split()]
    lemma = nltk.stem.wordnet.WordNetLemmatizer()
    query_terms_list = [lemma.lemmatize(t) for t in query_terms_list]

    answer = []

    # read in index files
    read_index_files()

    # get results
    #answer = retrieve_bool(query_terms)
    #answer = retrieve_vector(query_terms)
    answer = retrieve_vector(query_terms_list)

    # write results
    write_result_files()

    # print results
    print('Query: ', query_terms)
    i = 0
    for docid in answer:
        i += 1
        print(i, docids[docid])    

# Name:         read_index_files()
# Function:     Read data needed for retrieval in from external files and store the data in internal data structures
# Parameters:   None
# Returns:      None
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
    global snippets
    # open the files
    in_d = open('Final_System/docids.txt', 'r')
    in_v = open('Final_System/vocab.txt', 'r')
    in_p = open('Final_System/postings.txt', 'r')
    in_dl = open('Final_System/doclength.txt', 'r')
    # load the
    print('loading docids')
    docids = json.load(in_d)
    print('loading vocab')
    vocab = json.load(in_v)
    print('loading postings')
    postings = json.load(in_p)
    print('loading doclengths')
    doclength = json.load(in_dl)
    print('loading doctitles')
    with open('Final_System/doctitles.csv', newline='') as titles:
        reader = csv.DictReader(titles)
        for row in reader:
            for key, val in row.items():
                doctitles[key] = val
    print('loading docheaders')
    with open('Final_System/docheaders.csv', newline='') as headers:
        reader = csv.DictReader(headers)
        for row in reader:
            for key, val in row.items():
                docheaders[key] = val
    with open('Final_System/snippets.csv', newline='') as snippet:
        reader = csv.DictReader(snippet)
        for row in reader:
            for key, val in row.items():
                snippets[key] = val
    # close the files
    in_d.close()
    in_v.close()
    in_p.close()
    in_dl.close()

    return

# Name:         write_result_files()
# Function:     Write out retrieved documents to external files for further analysis
# Parameters:   None
# Returns:      None
def write_result_files():
    # declare refs to global variables
    global results

    w = csv.writer(open("results.csv", "w"))
    
    for key,val in enumerate(results):
        w.writerow([key, val])

    return

# Name:         clean_query()
# Function:     Clean the query so that it matches the vocabulary as much as possible
# Parameters:   query_terms - [string] - terms that will be searched in the index for
# Returns:      cleantext - string - cleaned text that can then be used in retrieval
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

# Name:         retrieve_vector()
# Function:     Find the most relevant documents to the query_terms within the index
# Parameters:   query_terms - [string] - terms that will be searched in the index for
# Returns:      answer - [string] - list of docids 
def retrieve_vector(query_terms):
    global docids
    global vocab
    global postings
    global docheaders
    global doctitles
    global snippets
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

        for doc, snippetWords in enumerate(snippets):
            if term in snippetWords:
                idf[termid] = float(idf.get(termid)) * float(1.75)
    
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
