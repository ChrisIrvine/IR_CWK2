import sys
import re
import string
import json
import csv
import nltk
import itertools
from nltk.corpus import wordnet

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []
doclength = {}
doctitles = {}
docheaders = {}
docNum = 0

# main is used for offline testing only
def main():
    # code for testing offline
    if len(sys.argv) != 2:
        print('usage: ./indexer.py file')
        sys.exit(1)
    filename = sys.argv[1]

    try:
        input_file = open(filename, 'r')
    except (IOError) as ex:
        print('Cannot open ', filename, '\n Error: ', ex)

    else:
        page_contents = input_file.read()  # read the input file
        url = 'http://www.' + filename + '/'
        print(url, page_contents)
        make_index(url, page_contents)

    finally:
        input_file.close()

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
    # load the
    print('loading docids...')
    docids = json.load(in_d)
    print('loading vocab...')
    vocab = json.load(in_v)
    print('loading postings...')
    postings = json.load(in_p)
    print('loading doclength...')
    doclength = json.load(in_dl)
    print('loading doctitles...')
    with open('doctitles.csv', newline='') as titles:
        reader = csv.DictReader(titles)
        for row in reader:
            for key, val in row.items():
                doctitles[key] = val
    print('loading docheaders...')
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

def write_index():
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclength
    global doctitles
    global docheaders

    # writes to index files: docids, vocab, postings and doclength
    try:
        outlist1 = open('docids.txt', 'w')
        outlist2 = open('vocab.txt', 'w')
        outlist3 = open('postings.txt', 'w')
        outlist4 = open('doclength.txt', 'w')
        titles = csv.writer(open('doctitles.csv', 'w'))
        headers = csv.writer(open('docheaders.csv', 'w'))

        json.dump(docids, outlist1)
        json.dump(vocab, outlist2)
        json.dump(postings, outlist3)
        json.dump(doclength, outlist4)

        for key, val in doctitles.items():
            titles.writerow([key, val])

        for key, val in docheaders.items():
            headers.writerow([key, val])

        outlist1.close()
        outlist2.close()
        outlist3.close()
        outlist4.close()
    except:
        with open('docids.txt', 'w') as a:
            for chunk in json.JSONEncoder().iterencode(docids):
                a.write(chunk)
        with open('vocab.txt', 'w') as b:
            for chunk in json.JSONEncoder().iterencode(vocab):
                b.write(chunk)

        post1 = {key: value for i, (key, value) in enumerate(postings.items()) if i % 2 == 0}
        post2 = {key: value for i, (key, value) in enumerate(postings.items()) if i % 2 == 1} 
        with open('postings.txt', 'w') as c:
            for chunk in json.JSONEncoder().iterencode(post1):
                c.write(chunk)
        with open('postings.txt', 'a') as c:
            for chunk in json.JSONEncoder().iterencode(post2):
                c.write(chunk)

        with open('doclength.txt', 'w') as d:
            for chunk in json.JSONEncoder().iterencode(doclength):
                d.write(chunk)
        for key, val in doctitles.items():
            titles.writerow([key, val])

        for key, val in docheaders.items():
            headers.writerow([key, val])
            
    return

# Function:     clean_html(page_contents)
# Parameters:   String - page_contents (source code of scraped webpage)
# Purpose:      Strips out all unwanted content from the raw page text of a
#               Web Page. Removes HTML tag, internal tag content, numbers,
#               abbreviations and punctuation through regex. Aims to preserve
#               external tag content.
# Returns:      String - cleantext
def clean_html(url, page_contents):
    global docheaders
    global doctitles
    # function to clean html
    #Seperate content from Title Tags
    try:
        doc_title_txt = re.findall('<title>(.*?)</title>', page_contents)
        doctitles[url] = []
        try:
            for t in range(0, len(doc_title_txt)):
                doc_title_txt[t] = clean_text(doc_title_txt[t])
                doc_title_txt[t] = [a.lower() for a in doc_title_txt[t].split()]
                doctitles[url].append(doc_title_txt[t])
        except:
            print('No title found')
        cleantext = re.sub('<title>(.*?)</title>', '', page_contents)
        #Seperate content from Header Tags
        doc_header_txt = re.findall('<h\d>(.*?)</h\d>', page_contents)
        docheaders[url] = []
        for t in range(0, len(doc_header_txt)):
            doc_header_txt[t] = clean_text(doc_header_txt[t])
            doc_header_txt[t] = [a.lower() for a in doc_header_txt[t].split()]
        try:
            doc_header_txt[0] = [a for b in doc_header_txt for a in b]
            docheaders[url].append(doc_header_txt)
        except:
            print('No headers found')
        cleantext = re.sub('<h\d>(.*?)</h\d>', '', cleantext)
        #No JavaScript
        cleantext = re.sub('<script[\s\S]+?/script>', '', cleantext)
        #No CSS
        cleantext = re.sub('<style[\s\S]+?/style>', '', cleantext)
        #No Comments
        cleantext = re.sub('<!--[\s\S]+?-->', '', cleantext)
        #No noscript tags
        cleantext = re.sub('<noscript[\s\S]+?/noscript>', '', cleantext)
        #No Links
        cleantext = re.sub('<a[\s\S]+?>', '', cleantext)
        #No input content
        cleantext = re.sub('<\s*input[^>]+>', '', cleantext)
        #No span content
        cleantext = re.sub('<\s*span[^>]+>', '', cleantext)
        #No Table Headers
        cleantext = re.sub('<thead[\s\S]+?>', '', cleantext)
        cleantext = re.sub('<th[\s\S]+?>', '', cleantext)
        cleantext = clean_text(cleantext)
    except:
        print('[-- Avoided Memory Error --]')
    return cleantext

def clean_text(unclean_text):
    #No HTML
    cleantext = re.sub('<.*?>', ' ', unclean_text)
    #No Numbers
    cleantext = re.sub('(\d)', '', cleantext)
    #No HTML Special Characters
    cleantext = re.sub('&[^\s]*', '', cleantext)
    #No Abbreviations
    cleantext = re.sub('(n\'t\b)',' not', cleantext)
    cleantext = re.sub('(\'ll\b)',' will', cleantext)
    cleantext = re.sub('(I\'m)','I am', cleantext)
    cleantext = re.sub('(I\'ve)','I have', cleantext)
    cleantext = re.sub('(\w*\'\w*)', '', cleantext)
    #No Punctuation
    cleantext = re.sub('([\W]+)', ' ', cleantext)
    return cleantext 

# Function:     make_index(url, page_contents)
# Parameters:   String - url (the url of the page being scraped by PCcrawler.py
#               String - page_content (source code of the scraped webpage)
# Purpose:      Process the source code from a website, that is cleaned by
#               clean_text(page_contents), and creates index tables for future
#               retrieval.
# Returns:      No inherit returns, but outputs content into:
#                   - docids.txt
#                   - postings.txt
#                   - vocab.txt
def make_index(url, page_contents):
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclength
    global docNum
    
    cleanUrl = re.sub('http://', '', url)
    cleanUrl = re.sub('https://', '', cleanUrl)

    if cleanUrl not in docids:
        # first convert bytes to string if necessary
        try:
            if isinstance(page_contents, bytes):
                page_contents = page_contents.decode('utf-8', 'ignore')
        except:
            page_contents = ''

        print('===============================================')
        print('Num: ', docNum, '|| make_index: url = ', cleanUrl)
        print('===============================================')

        # Send the contents of the scraped page to be cleaned, store output in page_text
        page_text = clean_html(cleanUrl, page_contents)

        if len(page_text) == 0:
            return

        # This code runs for each URL, therefore important not to overwrite
        # existing data.

        # Store the URLs that are scraped in the docids file
        docids.append(cleanUrl)

        # Using list comprehension, create the tokens list:
        # - split page_text by spaces
        # - take each token in the separated page_text
        # - lower case each token
        # - store the lower case token in tokens
        tokens = [t.lower() for t in page_text.split()]

        # Using list comprehension; create the vocabulary list, to act like a set:
        # - for every token in tokens
        # - if token does not exist within vocab
        #   - add token into vocab
        # - else
        #   - move onto next token
        # - check the token length is greater than 1

        #snow = nltk.stem.SnowballStemmer('english')
        #vocab.extend([snow.stem(t) for t in tokens if t not in vocab if len(t)>1])   
        
        lemma = nltk.stem.wordnet.WordNetLemmatizer()
        tokens = [lemma.lemmatize(t) for t in tokens]
        doclength[docids.index(cleanUrl)] = len(tokens)        
        for token in tokens:
            if (token not in vocab):
                vocab.append(token)          

        #ps = nltk.stem.PorterStemmer()
        #vocab.extend([ps.stem(t) for t in tokens if t not in vocab if len(t)>1])

        # for each token in vocabulary, get the tokenID (using enumerate)
        for tokenID, token in enumerate(vocab):
            # if that tokenID does not exist within postings
            if tokenID not in postings:
                # create an empty list at that tokenID within postings
                postings[tokenID] = []
            # count the frequency of a token within tokens
            freq = tokens.count(token)
            # check that the token occurs at least once
            if freq != 0:
                # append that the occurrence of that token to the correct tokenID
                # entry in postings, with the relevant url source
                postings[tokenID].append([docids.index(cleanUrl), freq])

        docNum += 1
        return
    else: 
        print('===============================================')
        print(cleanUrl, ' has already been scanned')
        print('===============================================')
        return

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
