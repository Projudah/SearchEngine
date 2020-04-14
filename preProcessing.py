'''
Nichoals Allair 02/14/2020
Module 2 Corpus Pre Processing

Purpose:
Convert Documents into a formatted corpus.

Output:
A formatted corpus that will be used for dictionary building. Outputs a
physical file which will be saved in the root directory.  Conversion is
performed once and if a corpus already exists do not update it.

Format of Output:
DocID, Title, Description (content)

Each document should be uniquely identified with a docID.


'''
import json
import os.path
from bs4 import BeautifulSoup

# folder for corpus
folder1 = 'uoCorpus/'
folder2 = 'reutersCorpus/'


def pre_process_UO_courses():

    # initailizing arrays to be used to write csv
    docIds = []
    titles = []
    descriptions = []

    # import the UofO Course from the root directory
    coursesDocument = open("Data/UofO_Courses.html", encoding="utf8")
    # generage a soup from the raw html
    soup = BeautifulSoup(coursesDocument, 'html.parser')
    coursesDocument.close()  # close th reader for the html

    # create array of all the classes
    courses = soup.findAll("div", class_="courseblock")

    for course in courses:
        # parse the enirety of the Course Title from the HTML
        courseBlockTitle = course.find("p", class_="courseblocktitle noindent")
        # parse the Course Description from the HTML
        courseDesc = course.find("p", class_="courseblockdesc noindent")
        # parse the extra information which includes the structure of the course (lecture, lab ect...)
        courseExtra = course.find("p", class_="courseblockextra noindent")

        courseTitle = courseBlockTitle.text  # obtain the text from the Title
        # take only the course code as the ID
        docId = courseBlockTitle.text[0:8]
        # the rest of the text is the course name
        title = courseBlockTitle.text[9:]

        description = ''  # set description to empty and then add content if it exists
        try:
            if courseDesc.text is not None:
                # append the descriptio if it exists
                description = description + courseDesc.text
            if courseExtra.text is not None:
                # append the class info if its exist
                description = description + "\n" + courseExtra.text
        # set description to empty if the class has no description
        except AttributeError:
            description = description

        # anything which does not have "units" in the title must be a french class, or is not a class
        if "units" in title:
            docIds.append(docId)  # adding english ids
            titles.append(title)  # adding english titles
            descriptions.append(description)  # adding english description

    # writing CSV file
    # with open('uoCourses.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["DocID", "Title", "Description"])
    #     for i in range(len(docIds)):
    #         newRow = [docIds[i], titles[i], descriptions[i]]
    #         writer.writerow(newRow)
    os.mkdir(folder1)
    for id, aTitle, desc in zip(docIds, titles, descriptions):
        if isEnglish(id):
            filename = folder1+id+'.json'
            content = [id, aTitle, aTitle+' '+desc.strip()]
            with open(filename, 'w+') as f:
                json.dump(content, f)

# returns true if course code is french

def pre_processing_rueters():
    docIds = []
    titles = []
    descriptions = []
    startIndex = 0

    files = os.path.join(os.getcwd(), "Data/reuters")

    for filename in os.listdir(files):
         with open(os.path.join(files, filename), 'rb') as file:
            data = file.read()
            soup = BeautifulSoup(data, "html.parser")
            articles = soup.find_all('reuters')

            for index, article in enumerate(articles, 1):
                title = article.find('title').text if article.find(
                    'title') is not None else ""
                description = article.find('body').text if article.find(
                    'body') is not None else ""

                docIds.append(index + startIndex)
                titles.append(title)
                descriptions.append(description)

            startIndex += 1000

    os.mkdir(folder2)
    for id, aTitle, desc in zip(docIds, titles, descriptions):
        filename = folder2+str(id)+'.json'
        content = [id, aTitle, aTitle+' '+desc.strip()]
        with open(filename, 'w+') as f:
            json.dump(content, f)




def isEnglish(id):
    number = id.split(' ')[1]

    # if second number in course code is less than 5
    return number[1] < '5'


def run():
    # check to make sure the data has not already been parsed
    if not os.path.exists(folder1):
        pre_process_UO_courses()

    if not os.path.exists(folder2):
        pre_processing_rueters()


run()
