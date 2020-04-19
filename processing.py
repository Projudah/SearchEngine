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

uoIndexes = 'uoIndexes/'
reutIndexes = 'reutersIndexes/'
indexPath = 'invertedIndex.dat'
bigramPath = 'bigramIndex.dat'
lmPath = 'languageModel.dat'
allPath = 'allTerms.dat'
nullkey = '<null>'

stop=True
stem=True
norm=True


def getTerms(corpusPath):
    docTerms = []
    rawTerms = []
    fullTerms = []
    fullIds = []
    dirlist = os.listdir(corpusPath)
    tot = len(dirlist)
    count = 0
    print('getting terms')
    for docPath in dirlist:
        id = docPath[:-5]
        print((count/tot)*100,'%',end='\r')
        count +=1
        with open(corpusPath+docPath, 'r') as f:
            doc = json.load(f)

        docTerm, rawTerm = dictionary.build(id, doc[2], stop, stem, norm)
        docTerms.append(docTerm)
        rawTerms.append(rawTerm)
        
        term = dictionary.buildRaw(id, doc[2])
        if len(term) >0:
            fullTerms.append(term)
            fullIds.append(id)
    return docTerms, rawTerms, fullTerms, fullIds

def calculateTermWeight():
    return 1

def generateInvertedIndex(fileloc):
    print('\n generating inverted index in', fileloc)
    termsList, rawList, fullTerms, fullIds = getTerms(fileloc)

    invertedindex = {}

    tot = len(termsList)
    count = 0

    for doc in termsList:
        print((count/tot)*100,'%',end='\r')
        count += 1
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
    lmModel = generateLanguageModel(fullTerms, fullIds)
    allTerms = []
    for t in fullTerms: allTerms += t
    return invertedindex, bigramIndex, lmModel, allTerms

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
    print('bigram indexing...')
    bigramIndex = {}
    tot = len(termList)
    count = 0
    for doc in termList:
        print((count / tot) * 100, '%', end='\r')
        count += 1
        for term in doc:
            bigrams = generateBigrams(term)

            for gram in bigrams:
                if gram in bigramIndex:
                    if term not in bigramIndex[gram]:
                        bigramIndex[gram] = bigramIndex[gram] + [term]
                else:
                    bigramIndex[gram] = [term]
    return bigramIndex

def generateLanguageModel(termsList, ids):

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
    if not os.path.exists(uoIndexes):
        os.mkdir(uoIndexes)
        preProcessing.run()
        invertedIndex, bigramIndex, lm, all = generateInvertedIndex('uoCorpus/')

        with open(uoIndexes+indexPath, 'w+') as f:
            json.dump(invertedIndex, f)

        if not os.path.exists(uoIndexes+bigramPath):

            with open(uoIndexes+bigramPath, 'w+') as f:
                json.dump(bigramIndex, f)

        if not os.path.exists(uoIndexes+lmPath):
            with open(uoIndexes+lmPath, 'w+') as f:
                json.dump(lm, f)

        if not os.path.exists(uoIndexes+allPath):
            with open(uoIndexes+allPath, 'w+') as f:
                json.dump(all, f)

    #REUTERS

    if not os.path.exists(reutIndexes):
        os.mkdir(reutIndexes)
        preProcessing.run()
        invertedIndex, bigramIndex, lm, all = generateInvertedIndex('reutersCorpus/')

        with open(reutIndexes+indexPath, 'w+') as f:
            json.dump(invertedIndex, f)

        if not os.path.exists(reutIndexes+bigramPath):

            with open(reutIndexes+bigramPath, 'w+') as f:
                json.dump(bigramIndex, f)

        if not os.path.exists(reutIndexes+lmPath):
            with open(reutIndexes+lmPath, 'w+') as f:
                json.dump(lm, f)

        if not os.path.exists(reutIndexes+allPath):
            with open(reutIndexes+allPath, 'w+') as f:
                json.dump(all, f)

def retrieve(term, corpus=uoIndexes):
    process()
    with open(corpus+indexPath, 'r') as f:
        invertedIndex = json.load(f)
    if term in invertedIndex:
        return invertedIndex[term]
    return None  # {"N/a": {FREQ: 0, DOCS: []}}

def retrieveGram(term, corpus=uoIndexes):
    process()
    with open(corpus+bigramPath, 'r') as f:
        bigramIndex = json.load(f)
    if term in bigramIndex:
        return bigramIndex[term]
    return None

def getLMBigram(id, corpus='uofo'):
    process()
    corpus = uoIndexes if corpus == 'uofo' else reutIndexes
    with open(corpus+lmPath, 'r') as f:
        lmBigramIndex = json.load(f)
    if id in lmBigramIndex:
            return lmBigramIndex[id]
    return None  # {"N/a": {FREQ: 0, DOCS: []}}



# process()
# print(generateBigrams('woody', rightStart=False))
