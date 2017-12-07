import re
import sys
import csv
import copy
import numpy as plt
import matplotlib.pyplot as plt


results = {}
numDocs = 0
retrieved_doc_status = {}

def main():
    get_data()

def get_data():
    global results
    global numDocs
    global retrieved_doc_status
    input_file = csv.reader(open('results.csv','r'))
    for row in input_file:
        results[row[0]] = row[1]
    
    for key,val in results.items():
        val = (list(val.split(',')))
        print(re.findall('\d', val[2]))

    return

def p_ten():
    global retrieved_doc_status
    # retrieve the document status
    doc_stati = [0] * numDocs
    return

def graph():

    return

# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
