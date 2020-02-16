import nltk
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.corpus import stopwords

from nltk.stem.porter import *
porterStem = PorterStemmer()

def build(id, document):
    #tokenize
    tokens = nltk.word_tokenize(document)

    #convert to lowercase
    tokens = [word.lower() for word in tokens]

    #Normalize
    tokens = [normalize(t) for t in tokens]

    #remove stop words
    tokens = [t for t in tokens if t not in stopwords.words('english')]

    #stem
    tokens = [porterStem.stem(t) for t in tokens]

    #convert to dictionary, remove duplicates
    result = {}
    for token in tokens:
        result[token] = id

    return result

def normalize(token):
    token = token.replace('-',' ')
    token = token.replace('.','')
    return token
