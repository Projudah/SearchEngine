import dictionary
import preProcessing
import os
import json

FREQ = 'frequency'
DOCS = 'documents'
ID = 'id'
WEIGHT = 'weight'
COUNT = 'count'
BIGRAMS = 'bigrams'

indexPath = 'invertedIndex.dat'
bigramPath = 'bigramIndex.dat'
lmPath = 'languageModel.dat'
nullkey = '<null>'


def getTerms(corpusPath, raw = False):
    docTerms = []
    rawTerms = []

    for docPath in os.listdir(corpusPath):
        with open(corpusPath+docPath, 'r') as f:
            doc = json.load(f)

        if not raw:
            docTerm, rawTerm = dictionary.build(doc[0], doc[2])
            docTerms.append(docTerm)
            rawTerms.append(rawTerm)
        else:
            term = dictionary.buildRaw(doc[0], doc[2])
            docTerms.append(term)
            rawTerms.append(doc[0])
    return docTerms, rawTerms

def calculateTermWeight():
    return 1

def generateInvertedIndex():
    termsList, rawList = getTerms('corpus/')

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
    bigramIndex = generatebigramIndex(rawList)
    return invertedindex, bigramIndex

def generateBigrams(term, leftStart=True, rightStart=True):
    if leftStart:
        term = '+'+term
    if rightStart:
        term = term+'+'

    bigrams = []
    for index in range(1, len(term)):
        bigrams.append(term[index - 1: index+1])

    return bigrams

def generatebigramIndex(termList):
    bigramIndex = {}
    for doc in termList:
        for term in doc:
            bigrams = generateBigrams(term)

            for gram in bigrams:
                if gram in bigramIndex:
                    if term not in bigramIndex[gram]:
                        bigramIndex[gram] = bigramIndex[gram] + [term]
                else:
                    bigramIndex[gram] = [term]
    return bigramIndex

def generateLanguageModel():
    termsList, ids = getTerms('corpus/', raw=True)

    languageModel = {}

    for doc, docId in zip(termsList, ids):
        termCount={nullkey: len(doc)}

        for index in range(len(doc)-1):
            term = doc[index]
            term2 = doc[index+1]

            termId = term
            if termId in termCount:
                termCount[termId][COUNT] = termCount[termId][COUNT]+1
            else:
                termCount[termId]={COUNT: 1, BIGRAMS: {}}

            bigram = term+' '+term2

            if bigram in termCount[termId][BIGRAMS]:
                termCount[termId][BIGRAMS][bigram] = termCount[termId][BIGRAMS][bigram]+1
            else:
                termCount[termId][BIGRAMS][bigram] = 1

        termId = doc[-1]
        if termId in termCount:
            termCount[termId][COUNT] = termCount[termId][COUNT] + 1
        else:
            termCount[termId] = {COUNT: 1, BIGRAMS: {}}
        languageModel[docId] = termCount


    return languageModel

def process():
    # check to make sure the data has not already been parsed
    if not os.path.exists(indexPath):
        preProcessing.run()
        invertedIndex, bigramIndex = generateInvertedIndex()

        with open(indexPath, 'w+') as f:
            json.dump(invertedIndex, f)

        if not os.path.exists(bigramPath):

            with open(bigramPath, 'w+') as f:
                json.dump(bigramIndex, f)

    if not os.path.exists(lmPath):
        lm = generateLanguageModel()
        with open(lmPath, 'w+') as f:
            json.dump(lm, f)

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

def getLMBigram(id):
    process()
    with open(lmPath, 'r') as f:
        lmBigramIndex = json.load(f)
    if id in lmBigramIndex:
            return lmBigramIndex[id]
    return None  # {"N/a": {FREQ: 0, DOCS: []}}



process()
# print(generateBigrams('woody', rightStart=False))
