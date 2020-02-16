import interface


def parseQuery(query):
    subQuery = ''
    part = ''
    index = 0
    returnList = []
    for i in range(len(query)):
        char = query[i]
        if char is '(':
            subList, part = parseQuery(query[index+1:])
            part = '('+part
            print('internal:', part)
            subQuery += part
            print('new sub:', subQuery)
            index += len(part)
        elif char is ')':
            return parseBoolean(subQuery, returnList, part), subQuery+')'
        else:
            subQuery += char
        index += 1

    return parseBoolean(subQuery, returnList, part), subQuery


def parseBoolean(query, retList, alreadyParsed=''):
    booleanType = ''
    if alreadyParsed in query and alreadyParsed != '':
        parts = query.split(alreadyParsed)
        query = parts[0].strip() if parts[0] != '' else parts[1].strip()

        if 'AND' in query:
            booleanType = 'AND'
            parts = query.split('AND')
            query = parts[0].strip() if parts[0] != '' else parts[1].strip()
        elif 'OR' in query:
            booleanType = 'OR'
            parts = query.split('OR')
            query = parts[0].strip() if parts[0] != '' else parts[1].strip()
        elif 'AND_NOT' in query:
            booleanType = 'AND_NOT'
            parts = query.split('AND_NOT')
            query = parts[0].strip() if parts[0] != '' else parts[1].strip()

    # print(query, booleanType, alreadyParsed)
    return []


if __name__ == '__main__':
    # interface.start()
    parseQuery('good AND ((great OR bad) OR boobies)')
