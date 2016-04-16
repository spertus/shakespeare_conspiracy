#Script to run a naive Bayes to learn two bodies of work, then compare two books to determine which is more likely written by which author.
#Reference texts must be put in "Samples" directory with format "author_text.txt"
import re
import string
import operator
from prettytable import PrettyTable
from sh import find
import math

#Format: "author1, author2, ..."
#possible options right now "joyce","conrad","austen", "wilde","shakespeare"
authors = ["austen","joyce","conrad"]

#input book files 
book_files = ["heartofdarkness.txt","ulysses.txt","prideandprejudice.txt"]

#IMPORTANT: text files to learn should be in the format: "author1_book.txt"


#Functions to get text files into tokenized, enumerated format 
def remove_punctuation(s):
    "see http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python"
    table = string.maketrans("","")
    return s.translate(table, string.punctuation)
 
def tokenize(text):
    text = remove_punctuation(text)
    text = text.lower()
    return re.split("\W+", text)
 
def count_words(words):
    wc = {}
    for word in words:
        wc[word] = wc.get(word, 0.0) + 1.0
    return wc

#Initiate data structures. 
#vocab holds word totals across writers.
#priors is simply how  many books were written by a given author over total books
vocab = {}
word_counts = {}
priors = {}
for i in authors:
    word_counts[i] = {}
    priors[i] = 0.0

docs = []

#find("Samples") prints a list with entries like: "Samples/austen_emma.txt" from which we want only "austen"
#If sample texts are not in "Samples" directory, need to change arg to find().
#Would also need to change indices to work.split() in author_work to grab only the author.
for work in find("Samples"):
    work = work.strip()
    author_work = work.split("_")[0][8:len(work.split("_")[0])]
    #Reject anything that's not a text file or not by one of our authors
    if work.endswith(".txt") == False or author_work not in authors:
        continue
    #Categorize by author
    else: 
        for i in authors:    
            if i in work:
                category = i    
    docs.append((category, work))
    #Record how many books by each author for priors
    priors[category] += 1
    #Open actual work, get word counts, and store in word_counts dict under each author.
    text = open(work, "r").read()
    words = tokenize(text)
    counts = count_words(words)
    for word, count in counts.items():
        if word not in vocab:
            vocab[word] = 0.0
        if word not in word_counts[category]:
            word_counts[category][word] = 0.0
        vocab[word] += count
        word_counts[category][word] += count

#Initialize structure for books to be estimated and read in word counts.
counts_combined = {}
for i in book_files: 
    book = open(i, "r").read()
    counts_combined[i] = count_words(tokenize(book))


#determine actual priors from counts and initialize log_probs which will hold probabilities for each author.
prior_authors = {}
log_probs = {}
for writer in authors:
    prior_authors[writer] = priors[writer] / sum(priors.values())
    log_probs[writer] = 0.0
print prior_authors

#Initalize scores which will store "posteriors" for each author and book.
scores = {}
for i in book_files:
    scores[i] = {} 

#Cycle through each book 
for i in counts_combined.keys():
    #Cycle through each word in the book and its count
    for w, cnt in counts_combined[i].items():
        if len(w) <= 3 or w not in vocab:
            #vocab[w] = 0.0
            #word_counts[category][word] = 0.0
            #vocab[w] += count
            #word_counts[category][word] += count
            continue
        #Marginal probability of that word across all authors
        p_word = vocab[w] / sum(vocab.values())
        p_w_given_author = {}
        #cycle through each author
        for writer in authors:
            #Probability of that word given the author = how many times that author uses the word over total uses by all authors 
            p_w_given_author[writer] = word_counts[writer].get(w, 0.0) / sum(word_counts[writer].values())
            #assume independence and as long as prob is greater than 0, multiply total uses by probability over marginal.
            if p_w_given_author[writer] > 0:
                log_probs[writer] += math.log(cnt * p_w_given_author[writer] / p_word)    
            #account for prior by adding to likelihood/marginal (log space)
            scores[i][writer] = (log_probs[writer] + math.log(prior_authors[writer]))
    #reset log_probs for new book            
    log_probs = dict.fromkeys(log_probs, 0)

#Print out results.
for i in scores:
    for j in authors:
        print "Log Score:", i, "by", j, ":", scores[i][j]
    print "Best estimate:", max(scores[i].iteritems(), key = operator.itemgetter(1))[0]

#Authors Test:

#Log Score: ulysses.txt by austen : 9642.80702934
#Log Score: ulysses.txt by conrad : 14932.2173448
#Log Score: ulysses.txt by joyce : 17500.5657755
#Log Score: ulysses.txt by shakespeare : 10033.0624186
#Best estimate: joyce
#Log Score: prideandprejudice.txt by austen : 7153.27425347
#Log Score: prideandprejudice.txt by conrad : 5666.03909939
#Log Score: prideandprejudice.txt by joyce : 5565.07551535
#Log Score: prideandprejudice.txt by shakespeare : 4445.20736575
#Best estimate: austen
#Log Score: hamlet.txt by austen : 1485.07494488
#Log Score: hamlet.txt by conrad : 2390.74121565
#Log Score: hamlet.txt by joyce : 2521.26483009
#Log Score: hamlet.txt by shakespeare : 4279.33267111
#Best estimate: shakespeare
#Log Score: heartofdarkness.txt by austen : 2025.94770753
#Log Score: heartofdarkness.txt by conrad : 5129.62954923
#Log Score: heartofdarkness.txt by joyce : 3609.35070408
#Log Score: heartofdarkness.txt by shakespeare : 2721.69724393
#Best estimate: conrad

#Shakespeare Conspiracy Test:

#Log Score: macbeth.txt by bacon : 900.979009441
#Log Score: macbeth.txt by marlowe : 2109.01760165
#Log Score: macbeth.txt by jonson : 1328.89977797
#Best estimate: marlowe
#Log Score: juliuscaesar.txt by bacon : 1235.75172668
#Log Score: juliuscaesar.txt by marlowe : 1917.26873699
#Log Score: juliuscaesar.txt by jonson : 1793.3410116
#Best estimate: marlowe
#Log Score: hamlet.txt by bacon : 1758.60057006
#Log Score: hamlet.txt by marlowe : 2568.39370564
#Log Score: hamlet.txt by jonson : 2564.34610823
#Best estimate: marlowe
#Log Score: kinglear.txt by bacon : 1476.00847081
#Log Score: kinglear.txt by marlowe : 2459.11011593
#Log Score: kinglear.txt by jonson : 2447.74485476
#Best estimate: marlowe
#Log Score: romeoandjuliet.txt by bacon : 1339.0301033
#Log Score: romeoandjuliet.txt by marlowe : 2676.93833073
#Log Score: romeoandjuliet.txt by jonson : 2373.05048049
#Best estimate: marlowe
#Log Score: othello.txt by bacon : 1133.18352159
#Log Score: othello.txt by marlowe : 2379.71496655
#Log Score: othello.txt by jonson : 1731.50711955
#Best estimate: marlowe
#Log Score: shakescompleteworks.txt by bacon : 18703.8356354
#Log Score: shakescompleteworks.txt by marlowe : 21570.1923297
#Log Score: shakescompleteworks.txt by jonson : 23070.4888151
#Best estimate: jonson





