import nltk


from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')
# nltk.download()

porterStem = PorterStemmer()


def build(id, document):
    # tokenize
    tokens = parseWords(document)

    # convert to dictionary, remove duplicates
    result = {}
    for token in tokens:
        result[token] = id

    return result


def normalize(token):
    # print('old:', token)
    token = token.replace('.', '')
    token = token.replace('-', ' ').strip()
    return nltk.word_tokenize(token)[0] if token != '' else ''


def parseWords(words):
    tokens = nltk.word_tokenize(words)

    # convert to lowercase
    tokens = [word.lower() for word in tokens]

    # Normalize
    tokens = [normalize(t) for t in tokens if t != '']

    # remove stop words
    tokens = [t for t in tokens if t not in stopwords.words('english')]

    # stem
    tokens = [porterStem.stem(t) for t in tokens]

    return tokens
