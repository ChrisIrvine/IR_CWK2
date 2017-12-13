# File:     evaluator.py
# Function: Run statistical analysis on the results from a series of queries of systems. Producing statistics and graphs.

import copy
import numpy as np
import matplotlib.pyplot as plt

# In retriever.py make a method to output the 1st 100 results from a query
# 1 == relevant, 0 == not relevant

# Set global variables
results = {}
nDocs = 0
nQueries = 0
retrieved_doc_status = {}
total_rel_array = []

# Name:     main()
# Function: Run statistical analysis, can toggle on/off by commenting out the method calls.
def main():
    get_data()
    #make_graphs()
    comparison_graphs()

# Name:         get_data()
# Function:     Read in the data from external files into global dictionaries. Progress is displayed to the command line.
# Parameters:   None
# Returns:      None
def get_data():
    # Include global varialbes
    global nQueries
    global retrieved_doc_status
    global nDocs
    # f = open('retrieval_results.txt', 'r')
    f = open('system_comparison.txt', 'r')
    # Iterate through the file and read the data in line by line
    for line in f:
        thisLine = line.strip()
        lineItems = thisLine.split()
        retrieved_doc_status[nDocs] = [int(i) for i in lineItems[0:len(lineItems)]]
        # Calculate number of docs returned
        nDocs += 1
    print("Read %d retrieved document status lines from file" % nDocs)
    # Calcualate number of queries in file
    nQueries = len(retrieved_doc_status[0])

    return

# Name:         comparison_graphs()
# Function      Generate graphs that compare two or more systems against each other.
# Parameters:   None
# Returns:      None
def comparison_graphs():
    # Include global variables
    global nQueries
    global retrieved_doc_status
    global nDocs

    # Create dictionary for all the comparison results to be included in the graphs
    comparison_dict = {}

    # Iterate through the file comparing the 4 systems,  uses same mathmatical steps as make_graphs()
    i = 0 
    for i in range(0, 4): 
        query_status = [i]*nDocs
        for doc in retrieved_doc_status.keys():
            query_status[doc] = retrieved_doc_status[doc][i]
        
        total_rel = sum(query_status)
        rel_after_i_seen = np.cumsum(query_status)

        precision = [i]*nDocs
        recall = [i]*nDocs
        fScore = [i]*nDocs
        for j in range(0, 10):
            precision[j] = rel_after_i_seen[j] / (j+1)
            recall[j] = rel_after_i_seen[j] / total_rel
            fScore[j] = 2*precision[j]*recall[j] / (precision[j] + recall[j])

        comparison_dict[i] = [precision, recall, fScore]

        smoothed_precision = copy.copy(precision)
        max_precision = precision[nDocs-1]
        for j in range(nDocs-1, 0, -1):
            if precision[i] < max_precision:
                smoothed_precision[j] = max_precision
            else:
                max_precision = precision[j]

        recall_points = np.linspace(0.0, 1.0, num=11)
        av_11pt_precision = []
        for thisRecallPoint in recall_points:
            nearestRecallValue = min(recall, key=lambda x:abs(x-thisRecallPoint))
            nearestRecallIndex = recall.index(nearestRecallValue)
            # print('Nearest recall value to %.2f is %.2f, index no %d' % (thisRecallPoint, nearestRecallValue, nearestRecallIndex))
            av_11pt_precision.append(smoothed_precision[nearestRecallIndex])

        comparison_dict[i].append(av_11pt_precision)
        comparison_dict[i].append(recall_points)

    pltPrecision1 = comparison_dict[0][0]
    pltRecall1 = comparison_dict[0][1]
    pltFScore1 = comparison_dict[0][2]
    pltAverage1 = comparison_dict[0][3]
    pltRecallPoints1 = comparison_dict[0][4]

    pltPrecision2 = comparison_dict[1][0]
    pltRecall2 = comparison_dict[1][1]
    pltFScore2 = comparison_dict[1][2]
    pltAverage2 = comparison_dict[1][3]
    pltRecallPoints2 = comparison_dict[1][4]

    pltPrecision3 = comparison_dict[2][0]
    pltRecall3 = comparison_dict[2][1]
    pltFScore3 = comparison_dict[2][2]
    pltAverage3 = comparison_dict[2][3]
    pltRecallPoints3 = comparison_dict[2][4]

    pltPrecision4 = comparison_dict[3][0]
    pltRecall4 = comparison_dict[3][1]
    pltFScore4 = comparison_dict[3][2]
    pltAverage4 = comparison_dict[3][3]
    pltRecallPoints4 = comparison_dict[3][4]

    plt.figure()
    plt.plot(pltRecall1, pltPrecision1)
    plt.plot(pltRecall2, pltPrecision2)
    plt.plot(pltRecall3, pltPrecision3)
    plt.plot(pltRecall4, pltPrecision4)
    plt.xlabel('Recall', weight='bold')
    plt.ylabel('Precision', weight='bold')
    plt.title('Overall System Precision-Recall Curve')
    plt.legend(['Base System', 'Weighted System', 'Stemmed System', 'Final System'])
    plt.grid()
    plt.savefig('overall-rc.png')

    plt.figure()
    plt.plot(pltFScore1)
    plt.plot(pltFScore2)
    plt.plot(pltFScore3)
    plt.plot(pltFScore4)
    plt.xlabel('Document number', weight='bold')
    plt.ylabel('F-score', weight='bold')
    plt.title('Overall System FScore')
    plt.legend(['Base System', 'Weighted System', 'Stemmed System', 'Final System'])
    plt.grid()
    plt.savefig('overall-fs.png')

    plt.figure()
    plt.plot(pltRecallPoints1, pltAverage1)
    plt.plot(pltRecallPoints2, pltAverage2)
    plt.plot(pltRecallPoints3, pltAverage3)
    plt.plot(pltRecallPoints4, pltAverage4)
    plt.xlabel('Recall', weight='bold')
    plt.ylabel('Precision', weight='bold')
    #plt.legend(['Base System', 'Weighted System'])
    #plt.legend(['Base System', 'Stemmed System'])
    #plt.legend(['Base System', 'Final System'])
    plt.legend(['Base System', 'Weighted System', 'Stemmed System', 'Final System'])
    plt.title('11-point interpolated average precision: Overall System Comparison')
    plt.grid()
    plt.savefig('p11-overall.png')
    
    return

# Name:         make_graphs
# Function      Generate graphs and statistical analysis that compare the accuracy of several search terms produced by a single system.
# Parameters:   None
# Returns:      None
def make_graphs():
    global nQueries
    global retrieved_doc_status
    global nDocs

    i = 0
    for i in range(0, 10):
        query_status = [i]*nDocs
        for doc in retrieved_doc_status.keys():
            query_status[doc] = retrieved_doc_status[doc][i]

        total_rel = sum(query_status)

        total_rel_array.append(total_rel)

        rel_after_j_seen = np.cumsum(query_status)

        precision = [i]*nDocs
        recall = [i]*nDocs
        fScore = [i]*nDocs
        for j in range(0, 100):
            precision[j] = rel_after_j_seen[j] / (j+1)
            recall[j] = rel_after_j_seen[j] / total_rel
            fScore[j] = 2*precision[j]*recall[j] / (precision[j] + recall[j])
            print('Docs %d, retrieval-value = %d, p = %.4f, r = %.4f, f = %.4f' % (j+1, query_status[j], precision[j], recall[j], fScore[j]))

        plt.figure()
        plt.rcParams.update({'font.size': 14})
        plt.plot(recall, precision, '-b+', label='Original precision-recall curve')
        plt.xlabel('Recall', weight='bold')
        plt.ylabel('Precision', weight='bold')
        plt.title('Precion versus Recall: Query %d' % (i+1))
        plt.grid()
        plt.savefig('Query%d_Recall.png' % (i+1))

        smoothed_precision = copy.copy(precision)
        max_precision = precision[nDocs-1]
        for j in range(nDocs-1, 0, -1):
            if precision[i] < max_precision:
                smoothed_precision[j] = max_precision
            else:
                max_precision = precision[j]

        # Plot the smoothed curve on top of the original
        plt.figure
        plt.plot(recall, smoothed_precision, '-r*', label='Smoothed precision-recall curve')
        plt.legend(loc='lower left')
        plt.xlabel('Recall', weight='bold')
        plt.ylabel('Precision', weight='bold')
        plt.title('Precion versus Recall (Smoothed): Query %d' % (i+1))
        plt.grid()
        plt.savefig('Query%d_Smooth.png' % (i+1))

        # Plot the F-score
        plt.figure()
        plt.plot(fScore, '-b+', label='F-score')
        plt.xlabel('Document number', weight='bold')
        plt.ylabel('F-score', weight='bold')
        plt.title('F-score: Query %d' % (i+1))
        plt.grid()
        plt.savefig('Query%d_FScore.png' % (i+1))

        # 11-point interpolated average precision
        recall_points = np.linspace(0.0, 1.0, num=11)
        av_11pt_precision = []
        for thisRecallPoint in recall_points:
            nearestRecallValue = min(recall, key=lambda x:abs(x-thisRecallPoint))
            nearestRecallIndex = recall.index(nearestRecallValue)
            # print('Nearest recall value to %.2f is %.2f, index no %d' % (thisRecallPoint, nearestRecallValue, nearestRecallIndex))
            av_11pt_precision.append(smoothed_precision[nearestRecallIndex])
        plt.figure()
        plt.plot(recall_points, av_11pt_precision, '-b+')
        plt.xlabel('Recall', weight='bold')
        plt.ylabel('Precision', weight='bold')
        plt.title('11-point interpolated average precision: Query %d' % (i+1))
        plt.grid()
        plt.savefig('Query%d_p11.png' % (i+1))

        cumSumQueryStatus = np.cumsum(query_status)
        precision_value = []

        for j in range(0, nDocs):
            if query_status[j] == 1:
                precision_value.append(cumSumQueryStatus[j]/(j+1))
            
        av_precision_value = np.mean(precision_value)
        print('Average precision value for this system on query no %d is %.4f' % (i, av_precision_value))

        sorted_doc_status = sorted(query_status, reverse=True)
        cumSumQueryStatusSorted = np.cumsum(sorted_doc_status)
        sorted_precision_value = []
        for j in range (0, nQueries):
            if sorted_doc_status[j] == 1:
                sorted_precision_value.append(cumSumQueryStatusSorted[j]/(j+1))
            
        thisQuery = [i]*nDocs
        allPrecisionValues = []
        for q in range(0, nQueries):
            for doc in retrieved_doc_status.keys():
                thisQuery[doc] = retrieved_doc_status[doc][q]
            thisCumSum = np.cumsum(thisQuery)

            precision_value = []
            for h in range(0, nDocs):
                if thisQuery[h] == 1:
                    precision_value.append(thisCumSum[h]/(h+1))
                    allPrecisionValues.append(thisCumSum[h]/(h+1))

            thisAverageValue = np.mean(precision_value)
            print('Average precision value for query no %d = %.4f' % (q+1, thisAverageValue))

        mean_average_precision = np.mean(allPrecisionValues)
        print('\nMEAN average precision value over all queries = %.4f' % mean_average_precision)

        print('==================================================================')
        print('END OF QUERY %d' % i)

    unrel_array = []

    for i in range(0, len(total_rel_array)):
        unrel_array.append(100-total_rel_array[i])

    ind = np.arange(nQueries)
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, total_rel_array, width, color='b')
    rects2 = ax.bar(ind + width, unrel_array, width, color='r')

    ax.set_ylabel('Number of Documents')
    ax.set_title('Relevant vs Irrelevant Docs per Query')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10'))
    ax.legend((rects1[0], rects2[0]), ('Relevant', 'Irrelevant'))
    plt.savefig('RelevantVsIrrelevant.png')


    return

# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
