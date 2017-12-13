from indexer import clean_html
from indexer import clean_text
import nltk
from nltk.corpus import wordnet

# Name:     main
# Function: Tests the indexing methods to double check one of the Queries that had a lower than expected result
def main():
    i = 0
    test_string =  '<title>Celebrating 30 years of Erasmus - Vice Chancellor&#039;s Blog - UEA</title><meta content="The cakes looked and tasted great, but it was the message on the icing that mattered most &#x2013; celebrating the 30th anniversary celebration of Erasmus at UEA." lang="en-GB" name="description" /><p>The cakes looked and tasted great, but it was the message on the icing that mattered most – celebrating the 30th anniversary celebration of Erasmus at UEA. And it coincided with Teresa May, once more engaging in discussions with her fellow EU leaders in Brussels over Britain’s Brexit deal. We can only hope that, whatever the final outcome of Brexit, the value of Erasmus will be recognised and the UK’s participation in it maintained.</p><p><img alt="cup cakes" src="/documents/3154295/7054672/Cup-Cakes.jpg/f3fba059-d7df-9464-452f-402b6808a79b?t=1508489318000" style="margin: 5px; float: left;" />Over 30 years, Erasmus has helped develop the skills of millions of Europeans and inspired educational innovation in thousands of teachers and practitioners. It has been the cornerstone of student mobility across Europe and generations of participants have benefitted from the clear vision of the European Commission. Individuals and institutions have gained enormously from engaging in the Erasmus scheme and many cite, directly, the correlation between their experiences, the skills gained and their own forward progression.</p><p>With more than 2,500 staff and students from UEA estimated to having participated on the programme, and a further 4,000 participants coming to UEA over the past 30 years, it is easy to see how the Erasmus programme has impacted on the University, not only within the Schools and Faculties, but also across the campus</p><p>Erasmus has continued to grow and evolve over the last 30 years and this is, in no small part, due to the amazing energy and enthusiasm of over 4 million participants, the staff who support them on their journeys, and the staunch commitment of the higher education sector. Together, this has helped create the most successful education exchange programme in the world.</p><p>Erasmus has been instrumental in building communication and openness to new possibilities, to inter-cultural understanding and co-operation between countries. By 2020 the Erasmus+ programme will have involved more than nine million students, apprentices, youth volunteers and staff. Sadly, loss of access to the Erasmus funding post-Brexit would greatly diminish the ability of UK students to study abroad elsewhere in the EU and for EU students to study abroad in the UK.</p><p>So, as the UK seeks to negotiate its future relationship with the EU, I do hope our negotiating stance is to maintain a strong commitment to continued engagement in Erasmus programmes, anchored in a new cooperation agreement with our European partners. I am passionate about present and future generations of young people being able to continue to enjoy and benefit from an Erasmus experience, and at UEA we will endeavour to create similar opportunities for students and staff post-Brexit, amid the uncertainty that entails.</p><p>The 30th anniversary event helped to showcase the pivotal role Erasmus has played, not only in supporting the UEA student experience, but also building capacity amongst our staff body, demonstrating our strategic commitment to internationalisation as a central feature of the University’s mission. I was delighted to be given a book of a collection of monologues by 30 alumni of the Erasmus programme at UEA and read what it meant to them. There is no doubt that Erasmus really was the icing on their UEA cake.</p></div>'
    print("Why didn't Erasmus appear in the vocabulary?")
    print("Running test html through indexer checks... ")
    print("=======================================================================")
    print(test_string)
    print("=======================================================================")
    test_string = clean_html('null', test_string)
    print("Test string minus HTML:")
    print("=======================================================================")
    print(test_string)
    print("=======================================================================")
    print("Splitting Test String into tokens...")
    print("=======================================================================")
    test_tokens = []
    test_tokens = [t.lower() for t in test_string.split()]
    print(str(test_tokens)[1:-1])
    print("=======================================================================")
    print("Stemming the tokens...")
    print("=======================================================================")
    lemma = nltk.stem.wordnet.WordNetLemmatizer()
    test_tokens = [lemma.lemmatize(t) for t in test_tokens]
    print(str(test_tokens)[1:-1])
    print("=======================================================================")
    print("Creating a vocabulary")
    print("=======================================================================")
    test_vocab = []
    for token in test_tokens:
            if (token not in test_vocab):
                test_vocab.append(token)
    print(str(test_vocab)[1:-1])        
    print("=======================================================================")
    print("Is erasmus in the vocabulary?")
    print("Using: if any(word in 'erasmus' for word in test_vocab)")
    print("=======================================================================")
    if any(word in "erasmus" for word in test_vocab):
        print("Yes, erasmus is present") 
    else:
        print("No, erasmus cannot be found")      

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()

#print "".join([str(x) for x in l] )
