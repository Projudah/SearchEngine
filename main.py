import interface
import processing
import dictionary
import argparse
import spellingCorrection

AND = ['AND', ' AND ']
OR = ['OR', ' OR ']
AND_NOT = ['AND_NOT', ' AND_NOT ']
WILD = '*'
LEFTBRACKET = '('
RIGHTBRACKET = ')'

relevant = {}

def toggleRelevance(query, id):
    if query in relevant:
        if id in relevant[query]:
            relevant[query].remove(id)
        else:
            relevant[query].append(id)
    else:
        relevant[query] = [id]

def isRelevant(query, id):
    if query in relevant:
        if id in relevant[query]:
            return True
    return False


def addPostMergeBrackets(array, join=AND[1]):
    if len(array) is 1:
        return array[0]
    else:
        center = len(array) // 2
        left = addPostMergeBrackets(array[:center], join)
        right = addPostMergeBrackets(array[center:], join)
        result = LEFTBRACKET + left + join + right + RIGHTBRACKET
        return result

class Query:
    def __init__(self, queryString, coll, type, isBigram=False):
        self.queryString = queryString
        self.isBigram = isBigram
        self.collection = coll
        self.type = type
        if isBigram:
            self.queryString = addPostMergeBrackets(queryString.split(' '))
            # print('BIGRAM!:',self.queryString)
        self.queryObject = self.parse(self.queryString)

    def checkSpelling(self):
        return self.queryObject.checkSpelling()


    def getBooleanType(self, term):
        if AND_NOT[0] in term: return AND_NOT[0]
        if OR[0] in term: return OR[0]
        if AND[0] in term: return AND[0]
        return None

    def getTerm(self, term, side, type):
        # print(term,'-', side,'-', type)
        term = term.strip()
        return term.split(type)[side].strip()

    def getSide(self, array):
        if array[1] is '' and array[0] is not '':
            return 0
        if array[0] is '' and array[1] is not '':
            return 1
        return None

    def getSubQueryObject(self, subQuery, left, right):
        if left and right:
            type = self.getBooleanType(subQuery.replace(left.string, '').replace(right.string, ''))
        elif left or right:
            parsed = left if left else right
            split = subQuery.split(LEFTBRACKET + parsed.string + RIGHTBRACKET)
            # print('parsed:', parsed.string)
            # print(subQuery, split, left, right)
            side = self.getSide(split)
            if not side:
                return parsed
            type = self.getBooleanType(split[side])
            term = self.getTerm(split[side], side, type)

            # separated into different statements for readability
            if side is 0:
                right = parsed
                left = Term(term, self.collection, self.type, self.isBigram)
            else:
                left = parsed
                right = Term(term, self.collection, self.type,  self.isBigram)
        else:
            type = self.getBooleanType(subQuery)
            if type:
                split = subQuery.split(type)
                left = Term(split[0].strip(), self.collection, self.type, self.isBigram)
                right = Term(split[1].strip(), self.collection, self.type, self.isBigram)
            else:
                left = Term(subQuery, self.collection, self.type, False)
        return SubQuery(subQuery, left, right, type)

    def parse(self, query):
        subQuery = ''
        i = 0
        left = None
        right = None
        while i < len(query):
            char = query[i]

            if char is LEFTBRACKET:
                subQueryObj = self.parse(query[i + 1:])
                if not left:
                    left = subQueryObj
                elif not right:
                    right = subQueryObj

                subQuery += LEFTBRACKET + subQueryObj.string + RIGHTBRACKET
                i += len(subQuery) - 1

            elif char is RIGHTBRACKET:
                return self.getSubQueryObject(subQuery, left, right)

            else:
                subQuery += char
            i += 1

        return self.getSubQueryObject(subQuery, left, right)

    def result(self):
        if self.isBigram:
            results = self.queryObject.result()
            resultsString = addPostMergeBrackets(results, join=OR[1])
            return Query(resultsString, self.collection, self.type).result()
        return self.queryObject.result()

class SubQuery:

    def __init__(self, string, leftSide = None, rightSide = None, booleanType=None):
        self.leftSide = leftSide
        self.rightSide = rightSide
        self.booleanType = booleanType
        self.string = string

    def orQuery(self):
        return list(set(self.leftSide.result()) | set(self.rightSide.result()))

    def andNotQuery(self):
        return list(set(self.leftSide.result()).difference(set(self.rightSide.result())))

    def andQuery(self):
        return list(set(self.leftSide.result()) & set(self.rightSide.result()))

    def checkSpelling(self):
        if self.leftSide and self.rightSide:
            return LEFTBRACKET + self.leftSide.checkSpelling() +' ' +self.booleanType+' '+ self.rightSide.checkSpelling() + RIGHTBRACKET
        return self.leftSide.checkSpelling() if self.leftSide else self.rightSide.checkSpelling()

    def result(self):
        if self.leftSide and self.rightSide:
            # print(self.leftSide.string, self.booleanType, self.rightSide.string)
            if self.booleanType is AND_NOT[0]:
                return self.andNotQuery()
            if self.booleanType is AND[0]:
                return self.andQuery()
            return self.orQuery()
        return self.leftSide.result() if self.leftSide else self.rightSide.result()

class Term:
    def __init__(self, string, collection, type, isBigram=False):
        self.string = string
        self.isWildCard = WILD in self.string
        self.isBigram = isBigram
        self.coll = collection
        self.collection = processing.uoIndexes if collection == 'uofo' else processing.reutIndexes
        self.type = type

    def expand(self):
        querySplit = self.string.split(WILD)
        leftBigram = processing.generateBigrams(querySplit[0], rightStart=False)
        rightBigram = processing.generateBigrams(querySplit[1], leftStart=False)

        bigramList = leftBigram + rightBigram
        bigramedQuery = ' '.join(bigramList)

        return bigramedQuery

    def convertToArray(self, dict):
        arr = []
        if not dict:
            return arr
        for doc in dict[processing.DOCS]:
            arr.append(doc[processing.ID])
        return arr

    def checkSpelling(self):
        choices, scores = spellingCorrection.getMatches(self.string, self.collection)
        minim = min(scores)
        closest = choices[scores.index(minim)]

        if minim < 2:
            return closest
        return self.string


    def result(self):

        if self.isWildCard:
            # print('wildcard:', self.string)
            expandedBigram = self.expand()
            # print(expandedBigram)
            return Query(expandedBigram, self.coll, self.type, isBigram=True).result()
        if self.isBigram:
            # print(self.string)
            return processing.retrieveGram(self.string, self.collection)
        ret = dictionary.parseWords(self.string)[0]
        token = ret[0] if len(ret) >0 else None
        return self.convertToArray(processing.retrieve(token, self.collection))

def query(query, coll, type):
    return Query(query.strip(' () '), coll, type).result()

def score(word, prevword, id):
    data = processing.getLMBigram(id)

    if not prevword:
        if word in data:
            return data[word][processing.COUNT]/data[processing.nullkey]
    else:
        if word in data and prevword in data:
            bigram = prevword+' '+word
            if bigram in data[prevword][processing.BIGRAMS]:
                score = data[prevword][processing.BIGRAMS][bigram]
                totPrev = data[prevword][processing.COUNT]
                return score/totPrev
    return 0

def getSuggestion(queryList, id, exclude=[]):
    lm = processing.getLMBigram(id)
    possibleWords = lm[queryList[-1]] if queryList[-1] in lm else None
    if possibleWords:
        bestword = None
        bestscore = None
        possibleWords = possibleWords[processing.BIGRAMS].keys()
        for posWord in possibleWords:
            posWord = posWord.split(' ')[1]
            scorelist = queryList + [posWord]
            runningScore = 1
            prevWord = None
            for word in scorelist:
                runningScore *= score(word, prevWord, id)
                prevWord = word
            # print(posWord, runningScore)
            if posWord not in exclude:
                bestword = bestword if bestscore and runningScore <= bestscore else posWord
                bestscore = bestscore if bestscore and runningScore <= bestscore else runningScore
        return bestword if bestscore else None
    return None

def cycleCompletion(n, query, id):
    wList = dictionary.parseAllWords(query)
    length = len(wList)
    result = []

    for i in range(n):
        step = 0
        #going forward
        word = None
        while not word and step < length:
            word = getSuggestion(wList[step:], id, result)
            step += 1

        #going backward
        step = length-1
        while not word and step > 0:
            word = getSuggestion(wList[:step], id, result)
            step -= 1

        add = [word] if word else []
        result += add

    return result

def complete(queryStr, coll, type):
    results = query(queryStr, coll, type)
    suggestions =[]
    num = len(results)

    if num >= 5:
        for res in results[:5]:
            suggestions += cycleCompletion(1, queryStr, res)
    elif num is 4:
        suggestions += cycleCompletion(2, queryStr, results[0])
        suggestions += cycleCompletion(1, queryStr, results[1])
        suggestions += cycleCompletion(1, queryStr, results[2])
        suggestions += cycleCompletion(1, queryStr, results[3])
    elif num is 3:
        suggestions += cycleCompletion(2, queryStr, results[0])
        suggestions += cycleCompletion(2, queryStr, results[1])
        suggestions += cycleCompletion(1, queryStr, results[2])
    elif num is 2:
        suggestions += cycleCompletion(3, queryStr, results[0])
        suggestions += cycleCompletion(2, queryStr, results[1])
    elif num is 1:
        suggestions += cycleCompletion(5, queryStr, results[0])
    return list(set(suggestions))

def synsAndHyps(word):
    syns, hyps = dictionary.getSynsHyps(word)
    expansion = syns[:3] + hyps[:2]
    return addPostMergeBrackets(expansion, join=OR[1])

def hasBool(string):
    if AND_NOT[0] in string: return True
    if OR[0] in string: return True
    if AND[0] in string: return True
    return False

def globalExpand(queryStr):
    if hasBool(queryStr): return None
    split = dictionary.parseAllWords(queryStr)
    newQuery = []
    for word in split:
        newQuery += [synsAndHyps(word)]
    return addPostMergeBrackets(newQuery)[1:-1] #join default to AND



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--nostop', action='store_true',
                        help="no stop words removal if true")
    parser.add_argument('-m', '--nostem', action='store_true',
                        help="no word stemming if true")
    parser.add_argument('-n', '--nonorm', action='store_true',
                        help="no word normalization if true")

    args = parser.parse_args()

    if args.nostop: processing.stop = False
    if args.nostem: processing.stem = False
    if args.nonorm: processing.norm = False

    processing.process()

    # q = Query('su*ort')
    # print(globalExpand('computer systems'))
    # print(expand('(*ge AND_NOT (man* OR health*))'))
    # print(query('ps*logy'))
    interface.start()
    # print(expand('computer info*'))
