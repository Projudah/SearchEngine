import interface
import processing
import dictionary


def expand(fullquery):
    splits = fullquery.split(' ')
    newquery = ''
    # print("uuu",splits)
    for query in splits:
        leftBracket = ''
        rightBracket = ''
        if '*' in query:
            # query = query.strip('(').strip(')')
            querySplit = query.split('*')
            # print(querySplit)
            leftBracket = '(' if '(' in querySplit[0] else ''
            rightBracket = ')' if ')' in querySplit[1] else ''
            leftBigram = processing.generateBigrams(
                querySplit[0].replace('(', '').strip(), rightStart=False) if querySplit[0].replace('(', '').strip() != '' else []
            rightBigram = processing.generateBigrams(
                querySplit[1].replace('(', '').strip(), leftStart=False) if querySplit[1].replace(')', '').strip() != '' else []

            bigrams = leftBigram + rightBigram
            words = andBigrams(bigrams)
            # print(query, bigrams, words)

            query = join(words) if words != [] else query.replace('*', '')

        space = '' if newquery == '' else ' '
        newquery += leftBracket+ (space+query)+ rightBracket
    # print(newquery)
    return newquery


def join(words):
    query = words[0]

    for i in range(1, len(words)):
        term = words[i]
        query = '('+query+' OR '+term+')'
    return query


def andBigrams(grams):
    res = []
    remove = []
    # print(grams)
    for gram in grams:
        terms = processing.retrieveGram(gram)
        # print(gram,':',terms)

        if len(res) == 0:
            res = terms
        else:
            for resTerm in res:
                if terms:
                    if resTerm not in terms:
                        remove.append(resTerm)
    for term in remove:
        if term in res:
            res.remove(term)
    return res

def query(query):
    return parseQuery(expand(query))

def parseQuery(query):
    # print('in',query)
    subQuery = ''
    part = ''
    index = 0
    returnList = []
    i = 0
    left=None
    right =None
    while i < len(query):
        char = query[i]
        # print('building:',subQuery)
        if char is '(':
            returnList, part = parseQuery(query[i+1:])
            if not left:
                left = [returnList, part]
            elif not right:
                right = [returnList, part]
            partLen = len(part)
            part = '('+part
            # print('internal:', part)
            subQuery += part
            # print('new sub:', subQuery)
            i += partLen
        elif char is ')':
            # print(parseBoolean(subQuery, returnList, part))
            if left and right:
                return parseBooleanResults(left, right, subQuery), subQuery+')'
            return parseBoolean(subQuery, returnList, part), subQuery+')'
        else:
            subQuery += char
        index += 1
        i += 1
    # print(parseBoolean(subQuery, returnList, part))
    if left and right:
        return parseBooleanResults(left, right, subQuery), subQuery
    return parseBoolean(subQuery, returnList, part), subQuery

def parseBooleanResults(left, right, query):
    subquery = query.split(left[1])[1].split(right[1])[0]

    result = []
    if 'AND' in subquery:
        for doc in left[0]:
            if doc in right[0]:
                result.append(doc)
    elif 'OR' in subquery:
        result = left[0]
        for doc in right[0]:
            if doc not in result:
                result.append(doc)
    elif 'AND_NOT' in subquery:
        for doc in left[0]:
            if doc not in right[0]:
                result.append(doc)

    return result


def parseBoolean(query, retList, alreadyParsed=''):
    booleanType = ''
    # print('running:',query)
    # print('already Ran:',alreadyParsed)
    # print('return from other:', retList,'\n')
    if alreadyParsed in query and alreadyParsed != '':
        if alreadyParsed == query:
            return retList
        parts = query.split(alreadyParsed)
        query = parts[0].strip() if parts[0] != '' else parts[1].strip()
        if 'AND' in query:
            booleanType = 'AND'
        elif 'OR' in query:
            booleanType = 'OR'
        elif 'AND_NOT' in query:
            booleanType = 'AND_NOT'
        # else: return

        if booleanType is '':
            return booleanSearchIndex(query)

        parts = query.split(booleanType)
        query = parts[0].strip() if parts[0] != '' else parts[1].strip()
        # print(query, booleanType, alreadyParsed)

        return booleanSearchIndex(query, booleanType, retList, parts[0] == '')

    else:
        if 'AND' in query:
            booleanType = 'AND'
        elif 'OR' in query:
            booleanType = 'OR'
        elif 'AND_NOT' in query:
            booleanType = 'AND_NOT'
        # else: return

        if booleanType is '':
            return booleanSearchIndex(query)
        parts = query.split(booleanType)
        leftQuery = parts[0].strip()
        rightQuery = parts[1].strip()

        rightList = booleanSearchIndex(rightQuery)
        # print(query, booleanType, alreadyParsed)

        return booleanSearchIndex(leftQuery, booleanType, rightList)


def booleanSearchIndex(query, booleanType=None, retList=None, reverse=False):
    if query == '':
        return []
    tokens = dictionary.parseWords(query)
    results = andQueries(tokens)

    if results and booleanType and retList:
        if booleanType is "AND":
            return booleanAnd(results, retList)
        elif booleanType is "OR":
            # print("the or part:", query)
            return booleanOr(results, retList)
        elif booleanType is "AND_NOT":
            return booleanAndNot(results, retList, reverse)

    elif results:
        return booleanOr(results, [])


def andQueries(tokens):
    if len(tokens) == 1:
        return processing.retrieve(tokens[0])
    else:
        res = processing.retrieve(tokens[0])
        for i in range(1, len(tokens)):
            tok = tokens[i]
            filter = processing.retrieve(tok)
            if not filter:
                res[processing.DOCS] = []
            else:
                for doc in res[processing.DOCS]:
                    found = False
                    for item in filter[processing.DOCS]:
                        if doc[processing.ID] == item[processing.ID]:
                            found = True
                    if not found:
                        res[processing.DOCS].remove(doc)
        return res


def booleanAnd(result, retList):
    collection = []
    for doc in result[processing.DOCS]:
        if doc[processing.ID] in retList:
            collection.append(doc[processing.ID])
    return collection


def booleanOr(result, retList):
    collection = retList
    for doc in result[processing.DOCS]:
        if doc[processing.ID] not in retList:
            collection.append(doc[processing.ID])
    return collection


def booleanAndNot(result, retList, reverse):
    collection = retList if reverse else []
    for doc in result[processing.DOCS]:
        if reverse:
            if doc[processing.ID] in retList:
                collection.remove(doc[processing.ID])
        else:
            if doc[processing.ID] not in retList:
                collection.append(doc[processing.ID])
    return collection


if __name__ == '__main__':
    # print(expand('(*ge AND_NOT (man* OR health*))'))
    # print(query('ps*logy'))
    interface.start()
    # print(expand('computer info*'))
