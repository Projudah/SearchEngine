import dictionary
import preProcessing
import os
import json

FREQ = 'frequency'
DOCS = 'documents'
ID = 'id'
WEIGHT = 'weight'

indexPath = 'invertedIndex.dat'

def getTerms(corpusPath):
    docTerms = []

    for docPath in os.listdir(corpusPath):
        with open(corpusPath+docPath,'r') as f:
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

def process():
    if not os.path.exists(indexPath): #check to make sure the data has not already been parsed
        preProcessing.run()
        invertedIndex = generateInvertedIndex()

        with open(indexPath, 'w+') as f:
            json.dump(invertedIndex, f)

process()