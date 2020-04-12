import interface
import processing
import dictionary

AND = ['AND', ' AND ']
OR = ['OR', ' OR ']
AND_NOT = ['AND_NOT', ' AND_NOT ']
WILD = '*'
LEFTBRACKET = '('
RIGHTBRACKET = ')'

class Query:
    def __init__(self, queryString, isBigram=False):
        self.queryString = queryString
        self.isBigram = isBigram
        if isBigram:
            self.queryString = self.addPostMergeBrackets(queryString.split(' '))
            # print('BIGRAM!:',self.queryString)
        self.queryObject = self.parse(self.queryString)

    def addPostMergeBrackets(self, array, join=AND[1]):
        if len(array) is 1:
            return array[0]
        else:
            center = len(array)//2
            left = self.addPostMergeBrackets(array[:center])
            right = self.addPostMergeBrackets(array[center:])
            result = LEFTBRACKET + left + join + right + RIGHTBRACKET
            return result


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
                left = Term(term, self.isBigram)
            else:
                left = parsed
                right = Term(term, self.isBigram)
        else:
            type = self.getBooleanType(subQuery)
            if type:
                split = subQuery.split(type)
                left = Term(split[0].strip(), self.isBigram)
                right = Term(split[1].strip(), self.isBigram)
            else:
                left = Term(subQuery, False)
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
            resultsString = self.addPostMergeBrackets(results, join=OR[1])
            return Query(resultsString).result()
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
    def __init__(self, string, isBigram=False):
        self.string = string
        self.isWildCard = WILD in self.string
        self.isBigram = isBigram

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

    def result(self):

        if self.isWildCard:
            # print('wildcard:', self.string)
            expandedBigram = self.expand()
            # print(expandedBigram)
            return Query(expandedBigram, isBigram=True).result()
        if self.isBigram:
            # print(self.string)
            return processing.retrieveGram(self.string)
        token = dictionary.parseWords(self.string)[0][0]
        return self.convertToArray(processing.retrieve(token))

def query(query):
    return Query(query).result()
if __name__ == '__main__':
    # q = Query('su*ort')
    # print(q.result())
    # print(expand('(*ge AND_NOT (man* OR health*))'))
    # print(query('ps*logy'))
    interface.start()
    # print(expand('computer info*'))
