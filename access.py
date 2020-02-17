import json
import os
import preProcessing
CHARCOUNT = 130
EX = 'excerpt'
TITLE = 'title'
FULL = 'full'
ID = 'id'

def getDoc(id):
    filename = preProcessing.folder+id+'.json'
    ret = 'Unavailable'
    try:
        with open(filename,'r') as f:
            ret = json.load(f)
    except:
        print('File not found')

    return ret

def getDocContent(id):
    doc = getDoc(id)
    excerpt = doc[2][:CHARCOUNT]+'...'
    return {
        ID: id,
        EX: excerpt,
        TITLE: doc[1],
        FULL: doc[2]
    }

def getAllDocs(idList):
    docList = []
    if idList:
        for id in idList:
            docList.append(getDocContent(id))

    return docList