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
    excerpt = doc[3][:CHARCOUNT]+'...'
    return {
        ID: id,
        EX: excerpt,
        TITLE: doc[2],
        FULL: doc[3]
    }

def getAllDocs(idList):
    docList = []

    for id in idList:
        docList.append(getDocContent(id))

    return docList