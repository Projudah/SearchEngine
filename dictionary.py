import nltk


from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')
# nltk.download()
from nltk.corpus import wordnet


porterStem = PorterStemmer()



def build(id, document, stop=True, stem=True, norm=True):
    # tokenize
    tokens, nonstemed = parseWords(document, stop, stem, norm)

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
    # print(words)
    tokens = nltk.word_tokenize(words)

    tokens = [word.lower() for word in tokens]

    tokens = [word.replace('.', '').replace(')', '').replace('(', '').replace(',', '').replace(' ', '-') for word in tokens ]

    return tokens


def parseWords(words, stop=True, stem=True, norm=True):
    tokens = nltk.word_tokenize(words)

    # convert to lowercase
    tokens = [word.lower() for word in tokens]

    # Normalize
    if norm: tokens = [normalize(t) for t in tokens if t != '']

    # remove stop words
    if stop: tokens = [t for t in tokens if t not in stopwords.words('english')]

    nonstemmed = tokens.copy()

    # stem
    if stem: tokens = [porterStem.stem(t) for t in tokens]

    return tokens, nonstemmed

def getSynsHyps(word):
    synonyms = [word]
    hypernyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
        for l in syn.hypernyms():
            hypernyms.append(l.lemmas()[0].name())


    return synonyms, hypernyms