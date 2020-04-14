import nltk


from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')
# nltk.download()

porterStem = PorterStemmer()


def build(id, document):
    # tokenize
    tokens, nonstemed = parseWords(document)

    # convert to dictionary, remove duplicates
    result = {}
    rawResult = {}
    for token in tokens:
        result[token] = id
    for token in nonstemed:
        rawResult[token] = id

    return result, rawResult

def buildRaw(id, document):
    tokens = parseAllWords(document)

    return tokens


def normalize(token):
    # print('old:', token)
    token = token.replace('.', '')
    token = token.replace('-', ' ').strip()
    return nltk.word_tokenize(token)[0] if token != '' else ''

def parseAllWords(words):
    tokens = nltk.word_tokenize(words)

    tokens = [word.lower() for word in tokens]

    tokens = [word.replace('.', '') for word in tokens]

    tokens = [word.replace(')', '') for word in tokens]

    tokens = [word.replace('(', '') for word in tokens]

    tokens = [word.replace(',', '') for word in tokens]

    tokens = [word.replace(' ', '-') for word in tokens]

    return tokens


def parseWords(words):
    tokens = nltk.word_tokenize(words)

    # convert to lowercase
    tokens = [word.lower() for word in tokens]

    # Normalize
    tokens = [normalize(t) for t in tokens if t != '']

    # remove stop words
    tokens = [t for t in tokens if t not in stopwords.words('english')]

    nonstemmed = tokens.copy()

    # stem
    tokens = [porterStem.stem(t) for t in tokens]

    return tokens, nonstemmed
