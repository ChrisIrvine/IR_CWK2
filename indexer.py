import sys
import re
import string
import json

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = {}

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


def write_index():
    # declare refs to global variables
    global docids
    global postings
    global vocab

    # writes to index files: docids, vocab, postings
    outlist1 = open('docids.txt', 'w')
    outlist2 = open('vocab.txt', 'w')
    outlist3 = open('postings.txt', 'w')

    json.dump(docids, outlist1)
    json.dump(vocab, outlist2)
    json.dump(postings, outlist3)

    outlist1.close()
    outlist2.close()
    outlist3.close()

    return

# Function:     clean_html(page_contents)
# Parameters:   String - page_contents (source code of scraped webpage)
# Purpose:      Strips out all unwanted content from the raw page text of a
#               Web Page. Removes HTML tag, internal tag content, numbers,
#               abbreviations and punctuation through regex. Aims to preserve
#               external tag content.
# Returns:      String - cleantext
def clean_html(page_contents):
    # function to clean html
    #No JavaScript
    cleantext = re.sub('<script[\s\S]+?/script>', '', page_contents)
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
    #No HTML
    cleantext = re.sub('<.*?>', ' ', cleantext)
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

def make_index(url, page_contents):
    for url in postings.keys():
        for word in postings[url].keys():
            if word in postings.keys():
                if url in postings[word].keys():
                    postings[word][url].extend(vocab[url][word][:])
                else:
                    postings[word][url] = vocab[url][word]
            else:
                postings[word] = {url: vocab[url][word]}
    return


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()