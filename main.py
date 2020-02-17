import interface
import processing
import dictionary


def expand(fullquery):
    splits = fullquery.split(' ')
    newquery = ''
    for query in splits:
        if '*' in query:
            query = query.strip('(').strip(')')
            querySplit = query.split('*')
            leftBigram = processing.generateBigrams(
                querySplit[0], rightStart=False)
            rightBigram = processing.generateBigrams(
                querySplit[1], leftStart=False)

            bigrams = leftBigram + rightBigram
            words = andBigrams(bigrams)

            query = join(words) if words != [] else query.replace('*', '')

        space = '' if newquery == '' else ' '
        newquery += space+query
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
    print(grams)
    for gram in grams:
        terms = processing.retrieveGram(gram)

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


def parseQuery(query):
    query = expand(query)
    subQuery = ''
    part = ''
    index = 0
    returnList = []
    i = 0
    while i < len(query):
        char = query[i]
        # print('building:',subQuery)
        if char is '(':
            returnList, part = parseQuery(query[index+1:])
            partLen = len(part)
            part = '('+part
            # print('internal:', part)
            subQuery += part
            # print('new sub:', subQuery)
            i += partLen
        elif char is ')':
            return parseBoolean(subQuery, returnList, part), subQuery+')'
        else:
            subQuery += char
        index += 1
        i += 1
    return parseBoolean(subQuery, returnList, part), subQuery


def parseBoolean(query, retList, alreadyParsed=''):
    booleanType = ''
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
        return booleanSearchIndex(leftQuery, booleanType, rightList)

    # print(query, booleanType, alreadyParsed)


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
    print(parseQuery('(*ge AND_NOT (man* OR health*))'))
    # interface.start()
    # print(expand('computer info*'))
