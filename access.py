import json
import os
import preProcessing
CHARCOUNT = 130
EX = 'excerpt'
TITLE = 'title'
FULL = 'full'
ID = 'id'
NAME = 'name'

def getDoc(id, coll):
    folder = preProcessing.folder1 if coll == 'uofo' else preProcessing.folder2
    filename = folder+id+'.json'
    ret = 'Unavailable'
    try:
        with open(filename,'r') as f:
            ret = json.load(f)
    except:
        print('File not found',id,coll)

    return ret

def getDocContent(id, coll):
    doc = getDoc(id, coll)
    excerpt = doc[2][:CHARCOUNT]+'...'
    return {
        ID: id,
        EX: excerpt,
        TITLE: doc[1],
        FULL: doc[2]
    }

def getAllDocs(idList, coll, type):
    docList = []
    if idList:
        for id in idList:
            docList.append(getDocContent(id, coll))

    return docList