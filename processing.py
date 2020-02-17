import dictionary
import preProcessing
import os
import json

FREQ = 'frequency'
DOCS = 'documents'
ID = 'id'
WEIGHT = 'weight'

indexPath = 'invertedIndex.dat'
bigramPath = 'bigramIndex.dat'


def getTerms(corpusPath):
    docTerms = []

    for docPath in os.listdir(corpusPath):
        with open(corpusPath+docPath, 'r') as f:
            doc = json.load(f)

        docTerm = dictionary.build(doc[0], doc[2])
        docTerms.append(docTerm)

    return docTerms


def calculateTermWeight():
    return 1


def generateInvertedIndex():
    termsList = getTerms('corpus/')

    invertedindex = {}

    for doc in termsList:
        for docTerm in doc:

            if docTerm in invertedindex:
                invertedindex[docTerm][FREQ] += 1
                entry = {
                    ID: doc[docTerm],
                    WEIGHT: calculateTermWeight()
                }
                invertedindex[docTerm][DOCS].append(entry)
            else:
                invertedindex[docTerm] = {
                    FREQ: 1,
                    DOCS: [{
                        ID: doc[docTerm],
                        WEIGHT: calculateTermWeight()
                    }]
                }
    return invertedindex


def generateBigrams(term, leftStart=True, rightStart=True):
    if leftStart:
        term = ' '+term
    if rightStart:
        term = term+' '

    bigrams = []
    for index in range(1, len(term)):
        bigrams.append(term[index - 1: index+1])

    return bigrams


def generatebigramIndex(invertedIndex):
    bigramIndex = {}
    for term in invertedIndex:
        bigrams = generateBigrams(term)

        for gram in bigrams:
            if gram in bigramIndex:
                bigramIndex[gram] = bigramIndex[gram] + [term]
            else:
                bigramIndex[gram] = [term]
    return bigramIndex


def process():
    # check to make sure the data has not already been parsed
    if not os.path.exists(indexPath):
        preProcessing.run()
        invertedIndex = generateInvertedIndex()

        with open(indexPath, 'w+') as f:
            json.dump(invertedIndex, f)

    if not os.path.exists(bigramPath):
        with open(indexPath, 'r') as f:
            invertedIndex = json.load(f)
        bigramIndex = generatebigramIndex(invertedIndex)

        with open(bigramPath, 'w+') as f:
            json.dump(bigramIndex, f)


def retrieve(term):
    process()
    with open(indexPath, 'r') as f:
        invertedIndex = json.load(f)
    if term in invertedIndex:
        return invertedIndex[term]
    return None  # {"N/a": {FREQ: 0, DOCS: []}}


def retrieveGram(term):
    process()
    with open(bigramPath, 'r') as f:
        bigramIndex = json.load(f)
    if term in bigramIndex:
        return bigramIndex[term]
    return None


process()
# print(generateBigrams('woody', rightStart=False))
