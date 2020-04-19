import json
import os.path
from bs4 import BeautifulSoup

#need a training set from documents which have a topic
#need a test set from documents which have no assigned topic

trainingSet = []
testSet = []
trainingTopics = []


def getDataFromRueters():
    files = os.path.join(os.getcwd(), "Data/reuters")
    for filename in os.listdir(files):
        with open(os.path.join(files, filename), 'rb') as file:
            data = file.read()
            soup = BeautifulSoup(data, "html.parser")
            articles = soup.find_all('reuters')

            for article in articles:
                topics = article.find('topics') if article.find('topics').find("d") is not None else ""
                body = article.find('body').text if article.find('body') is not None else ""

                if body is not "":
                    if topics is not "":
                       trainingSet.append(article)
                       trainingTopics.append(list(set(topics)))
                    else:
                        testSet.append(article)





getDataFromRueters()






