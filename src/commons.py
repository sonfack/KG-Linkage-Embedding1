"""
This module contains funcitons for general purpose on data
"""
import os
import gzip
import pickle
import logging
import numpy as np
import pandas as pd
from numpy import linalg
from chardet import detect
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer, TfidfVectorizer
from src.predefined import DATA_FOLDER, OUTPUT, MODEL, TEXT_FOLDER, GROUND_FOLDER, KB_FOLDER, TFIDFMODEL, TFMODEL, LISTOFPROPERTIES


englishStopWords = text.ENGLISH_STOP_WORDS

"""
Stop words
Build a liste of stop words base on personalize string and a list of english stop words form sklearn feature extraction text
"""
stoplist = "the to is a that and or . ; , - _ A ".split()+list(englishStopWords)


def readDataFile(fileName, folder="Texts"):
    """
    This function returns the data frame corresponding to a csv fille.
    If the folder is given, it create a full path to the file and reads it with pandas read_csv
    Else it considers that the full path is given at the parameter and reads the file directly
    """
    print("### fileName", len(fileName.split("/")))
    print(fileName)
    print("###")
    dataFile = ""
    if len(fileName.split("/")) >= 2:
        dataFile = pd.read_csv(fileName, sep='\t', encoding="utf-8")
    else:
        if folder in "Texts" and len(folder) == len("Texts"):
            completeFileName = os.path.join(TEXT_FOLDER, fileName)
            print("File name in Texts: ", completeFileName)
            dataFile = pd.read_csv(completeFileName, sep='\t')
            print("### data frame Texts")
            print(dataFile)
            print("###")
        elif folder in "Outputs" and len(folder) == len("Outputs"):
            completeFileName = os.path.join(OUTPUT, fileName)
            print("File name in Outputs: ", completeFileName)
            dataFile = pd.read_csv(completeFileName, sep='\t')
            print("### data frame Outputs")
            print(dataFile)
            print("###")
        elif folder in "Datasets" and len(folder) == len("Datasets"):
            completeFileName = os.path.join(KB_FOLDER, fileName)
            print("File name in Datasets: ", completeFileName)
            dataFile = pd.read_csv(completeFileName, sep='\t')
            print("### data frame Datasets")
            print(dataFile)
            print("###")
        elif folder in "Models" and len(folder) == len("Models"):
            completeFileName = os.path.join(MODEL, fileName)
            print("File name in Models: ", completeFileName)
            dataFile = pd.read_csv(completeFileName, sep='\t')
            print("### data frame Models")
            print(dataFile)
            print("###")
    dataFile = dataFile.fillna("")
    return dataFile


def readCompressDataFile(fileName, folder="Texts"):
    """
    Read our compress data. 
    """
    if folder in "Texts" and len(folder) == len("Texts"):
        completeFileName = os.path.join(TEXT_FOLDER, fileName)
    elif folder in "Output" and len(folder) == len("Output"):
        completeFileName = os.path.join(OUTPUT, fileName)
    elif folder in "Datasets" and len(folder) == len("Datasets"):
        completeFileName = os.path.join(KB_FOLDER, fileName)
    outputFile = os.path.join(OUTPUT, "newdata"+str(datetime.now()).replace(
        ":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv")
    with open(completeFileName, 'r') as f:
        for i, line in enumerate(f):
            for sl in line.split("\\n"):
                for tsl in sl.split("\\t"):
                    newdata = open(outputFile, "a+")
                    newdata.write(tsl)
                    newdata.write("\t")
                    newdata.close()
                newdata = open(outputFile, "a+")
                newdata.write("\n")
                newdata.close()


def createListOfTextFromListOfFileNameByColumn(fileName, columnName, folder="Texts"):
    """
    This function creates a list of text using a liste for file names and the columns that will 
    be used in each file.
    The list is created column by column, that is verticaly
    NB: the fileName is a liste of file names  and the columnName is either a liste of columns or a string.
    """
    listOfSentences = []
    # List of file names and list of columns
    if isinstance(columnName, list):
        dataFrame = readDataFile(fileName, folder)
        dataFrameColumns = dataFrame.columns.tolist()
        for columnN in columnName:
            sentences = []
            if columnN in dataFrameColumns:
                sentences = dataFrame[columnN]
                sentences.fillna("", inplace=True)
                sentences = sentences.values.tolist()
                listOfSentences.append(sentences)
        return listOfSentences
    # List of file names and a single column (a string)
    elif isinstance(columnName, str):
        dataFrame = readDataFile(fileName, folder)
        dataFrameColumns = dataFrame.columns.tolist()
        if columnName in dataFrameColumns:
            sentences = dataFrame[columnName]
            sentences.fillna("", inplace=True)
            sentences = sentences.values.tolist()
            listOfSentences.append(sentences)
        return listOfSentences


def createListOfTextFromListOfFileNameByRow(fileName, columnName=None, position=None, fileNameFolder="Texts"):
    """
    This function creates a list of text using a liste for file names and the columns that will 
    be used in each file.
    The list is created row by row, that is horizontaly
    NB: the fileName is a liste of file names  and the columnName is either a liste of columns or a string.

    position can be : 
    - [begin, end] an intervalle of rows to be used where begin and end are integers
    In this case a list of list is returned by the funciton 

    - value an integer specifying the exact entity to use 
    In this case a list of sentences is returned by the function 

    - None is the default value and by default all entities are used 
    In this case a list of list of sentences is returns by the function
    """
    listOfEntity = []
    if isinstance(columnName, list) and isinstance(fileName, str):
        dataFrame = readDataFile(fileName, fileNameFolder)
        dataFrameColumns = dataFrame.columns.tolist()
        # len(dataFrame): is the number of rows in the dataframe
        if position is None:
            listOfSentences = []
            listOfEntity = []
            rows, cols = dataFrame.shape
            for row in range(rows):
                sentences = []
                for columnN in columnName:
                    if columnN in dataFrameColumns:
                        sentences.append(dataFrame.loc[row, columnN])
                listOfSentences.append(sentences)
                if "entity" in dataFrameColumns:
                    listOfEntity.append(dataFrame.loc[row, "entity"])
            return listOfEntity, listOfSentences
        elif isinstance(position, int):
            listOfSentences = []
            sentences = []
            rows, cols = dataFrame.shape
            for columnN in columnName:
                if columnN in dataFrameColumns and position in range(rows):
                    sentences.append(dataFrame.loc[position, columnN])

            listOfSentences.append(sentences)
            listOfEntity.append(dataFrame.loc[position, "entity"])
            return listOfEntity, listOfSentences
        elif isinstance(position, list):
            listOfSentences = []
            for row in range(position[0], position[1]+1):
                sentences = []
                for columnN in columnName:
                    if columnN in dataFrameColumns:
                        sentences.append(dataFrame.loc[row, columnN])
                listOfSentences.append(sentences)
                listOfEntity.append(dataFrame.loc[row, "entity"])
            return listOfEntity, listOfSentences
    elif isinstance(columnName, str):
        dataFrame = readDataFile(fileName, fileNameFolder)
        dataFrameColumns = dataFrame.columns.tolist()
        print("### list of dataset columns")
        print(dataFrameColumns)
        print("###")
        if position is None:
            listOfSentences = []
            listOfEntity = []
            rows, cols = dataFrame.shape
            if columnName in dataFrameColumns:
                for row in range(rows):
                    sentences = []
                    sentences.append(dataFrame.loc[row, columnName])
                    listOfSentences.append(sentences)
                    if "entity" in dataFrameColumns:
                        listOfEntity.append(dataFrame.loc[row, "entity"])
                return listOfEntity, listOfSentences
        elif isinstance(position, int):
            listOfSentences = []
            if columnName in dataFrameColumns:
                sentences.append(dataFrame.loc[position, columnName])
                listOfSentences.append(sentences)
                listOfEntity.append(dataFrame.loc[position, "entity"])
            return listOfEntity, listOfSentences
        elif isinstance(position, list):
            listOfSentences = []
            if columnName in dataFrameColumns:
                for pos in range(position[0], position[1]+1):
                    if pos in range(rows) and columnName in dataFrameColumns:
                        sentences.append(dataFrame.loc[pos, columnName])
                    listOfSentences.append(sentences)
                    listOfEntity.append(dataFrame.loc[pos, "entity"])
            return listOfEntity, listOfSentences
    elif columnName is None:
        dataFrame = readDataFile(fileName, fileNameFolder)
        dataColumns = dataFrame.columns.tolist()
        print(dataColumns)
        listOfEntity, listOfSentences = createListOfTextFromListOfFileNameByRow(
            fileName, dataColumns, position, fileNameFolder)
        return listOfEntity,  listOfSentences


def createListOfText(fileName, columnName=None, position=None, by="row",  fileNameFolder="Texts"):
    """
       This function creates a list of text from a CSV file. 
       It uses the colunm given as parameter to get the text from that colunm. 
       If a list is given as file name the function will create a list of text from both files in the list base on the colunm name. 
       If columnName is a list, each element in the list corresponds to the colunm in the file at the same position at the fileName
       by = row/column indicates the direction on wich sets of documents will be red.
       if by = column then
    from top to down for each column cells are consider as documents
       if by = row then 
    from left to right for each row cells are consider as documents
    """
    # List of file names
    if isinstance(fileName, list):
        listOfInfo = []
        listOfEntities = []
        if by == "column":
            for fileN in fileName:
                entities, texts = createListOfTextFromListOfFileNameByColumn(
                    fileN, columnName, fileNameFolder)
                listOfEntities.append(entities)
                listOfInfo.append(texts)
            return listOfEntities, listOfInfo
        elif by == "row":
            for fileN in fileName:
                entities, texts = createListOfTextFromListOfFileNameByRow(
                    fileN, columnName, fileNameFolder)
                listOfEntities.append(entities)
                listOfInfo.append(texts)
            return listOfEntities, listOfInfo
    # A single file name
    elif isinstance(fileName, str):
        # A single file name and a list of columnName
        if by == "column":
            listOfEntities, listOfInfo = createListOfTextFromListOfFileNameByColumn(
                fileName, columnName, fileNameFolder)
            return listOfEntities, listOfInfo
        # A single file name and a single columnName
        elif by == "row":
            listOfEntities, listOfInfo = createListOfTextFromListOfFileNameByRow(
                fileName, columnName, position, fileNameFolder)
            return listOfEntities, listOfInfo


def createFrequencyModel(fileName, columnNameArg=None, position=None, by="row", to="KB", model="tfidf", fileNameFolder="Texts"):
    """
    This function creates a TF, IDF and TF-IDF  model and save them on files.   
    For a given model set the models parameter:
    - as a string eg : "TF", "IDF" or "TF-IDF"
    - as a list eg : ["TF", "IDF"]
    - as None
    If None is set to the model parameter, all the three models are created 
    for a list of models set the models parameter with the list of models to create 
    fileName is the file (csv) containing the data on wich the model will be created 
    columnName is the name or the list o column from wich the text will be extracted 
    by = row/column indicates the direction on wich sets of documents will be red.
    if by = column then
    from top to down for each column cells are consider as documents
    if by = row then 
    from left to right for each row cells are consider as documents 
    to=KB/TEXT
    """
    columnName = []
    if columnNameArg is None:
        columnName = LISTOFPROPERTIES
    elif isinstance(columnNameArg, str):
        columnName.append(columnNameArg)
        # listOfOneColumn = []
        # columnName = listOfOneColumn.append(olumnName)
    elif isinstance(columnNameArg, list):
        columnName = columnNameArg

    if isinstance(model, str):
        entities, listOfListOfText = createListOfText(
            fileName, columnName, position, by, fileNameFolder)
        print("### listOfListOfText")
        print(listOfListOfText)
        print("###")
        listOfText = []
        for ltext in listOfListOfText:
            print("### list of text")
            ltext = [str(text) for text in ltext if text]
            print(ltext)
            print("###")
            listOfText.append(" ".join(ltext))
        print("###")
        print(listOfText)
        print("###")
        tfCount = CountVectorizer(stop_words=stoplist)
        countMatrix = tfCount.fit_transform(listOfText)
        if model == "TF" or model == "tf" or model == "BOW":
            print("### TF")
            print(tfCount)
            print("###")
            print("### TF matrix")
            print(countMatrix)
            print("###")

            outputFileModel = to+by+"tfValue"+"_"+"Properties_"+"-".join(columnName)+"_"+model+"_"+str(
                datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]
            with open(os.path.join(MODEL, outputFileModel), "+wb") as f:
                pickle.dump(
                    {"vectorizer": tfCount, "countMatrix": countMatrix}, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            return 'Models', outputFileModel
        elif model == "idf" or model == "IDF":
            idfCount = TfidfTransformer()
            idfCount.fit(countMatrix)
            print("### IDF")
            print(idfCount)
            print("###")
            outputFileModel = to+by+"idfValue"+"_Properties_"+"-".join(columnName)+"_"+model+"_" + \
                str(datetime.now()).replace(":", "").replace(
                    "-", "").replace(" ", "").split(".")[0]
            with open(os.path.join(MODEL, outputFileModel), "+wb") as f:
                pickle.dump(
                    {"vectorizer": idfCount, "countMatrix": tfCount}, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            return "Models", outputFileModel
        elif model == "TF-IDF" or model == "tf-idf" or model == "tfidf" or model == "TFIDF":
            tfidfCount = TfidfVectorizer(stop_words=stoplist)
            tfIdfValue = tfidfCount.fit_transform(listOfText)
            print("### TF-IDF")
            print(tfidfCount)
            print("###")
            print("### TF-IDF VALUE")
            print(tfIdfValue)
            print("###")
            outputFileModel = to+by+"tfIdfValue"+"_Properties_"+"-".join(columnName)+"_"+model+"_" + \
                str(datetime.now()).replace(":", "").replace(
                    "-", "").replace(" ", "").split(".")[0]
            with open(os.path.join(MODEL, outputFileModel), "+wb") as f:
                pickle.dump(
                    {"vectorizer": tfidfCount, "countMatrix": tfIdfValue}, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            return "Models", outputFileModel
    elif isinstance(model, list) and len(model) > 0:
        newModel = model.pop()
        createFrequencyModel(fileName, columnName, model)
        createFrequencyModel(fileName, columnName, newModel)
    elif model is None:
        newModel = ["tf", "idf", "tfidf"]
        createFrequencyModel(fileName, columnName, by,
                             to, newModel, fileNameFolder)


def wordsImportance(modelFile, model, fileName, columnName=None, position=None, by="row", modelFileFolder="Models", fileNameFolder="Texts"):
    """
    This function creates a weighted file of words embedded, this is possible when the embeddedModel is given as parameter.
    embeddedModel contains the embedding if the words in the vocabulary
    model ={BOW or TF, TFIDF}
    We set default column to None
    """
    if model is not None:
        # BOW
        if model == "BOW" or model == "TF" or model == "tf":
            outputVocabularyFile = "WordImportance"+by+"vocabularyTFOf"+model+str(
                datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"
            listOfColumns = ["entity", "word", "tf"]
            cFile = open(os.path.join(OUTPUT, outputVocabularyFile), "w")
            cFile.write("\t".join(listOfColumns))
            cFile.write("\n")
            cFile.close()
            return "Outputs", outputVocabularyFile
        # IDF
        elif model == "IDF" or model == "idf":
            outputVocabularyFile = "WordImportance"+by+"vocabularyIDFOf"+model+str(
                datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"
            listOfColumns = ["word", "idf"]
            cFile = open(os.path.join(
                OUTPUT, outputVocabularyFile), "w")
            cFile.write("\t".join(listOfColumns))
            cFile.write("\n")
            cFile.close()
            return "Outputs", outputVocabularyFile
        # TF-IDF
        elif model == "TFIDF" or model == "tfidf" or model == "tf-idf" or model == "TF-IDF":
            outputVocabularyFile = "WordImportance"+by+"vocabularyTFIDFOf"+model+str(
                datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"
            listOfColumns = ["entity", "word", "tf-idf"]
            cFile = open(os.path.join(
                OUTPUT, outputVocabularyFile), "w")
            cFile.write("\t".join(listOfColumns))
            cFile.write("\n")
            cFile.close()

        entities, listOfText = createListOfText(
            fileName, columnName, position, by, fileNameFolder)

        # Read the model
        print("### model file")
        print(modelFile)
        print("###")
        modelFileDirectory = os.path.join(DATA_FOLDER, modelFileFolder)
        with open(os.path.join(modelFileDirectory, modelFile), "rb") as f:
            Model = pickle.load(f)
        f.close()
        vocabCount = Model["vectorizer"]
        countMatrix = Model["countMatrix"]
        if model == "idf" or model == "IDF":
            modelValue = vocabCount.idf_
            print("### features")
            modelVocabulary = countMatrix.get_feature_names()
            print(modelVocabulary)
            print("###")
            print("### values")
            print(modelValue)
            print("###")
            for value in range(len(modelVocabulary)):
                listOfValues = []
                listOfValues.append(str(modelVocabulary[value]))
                listOfValues.append(str(modelValue[value]))
                print("###")
                print(listOfValues)
                print("###")
                cFile = open(os.path.join(
                    OUTPUT, outputVocabularyFile), "a+")
                cFile.write("\t".join(listOfValues))
                cFile.write("\n")
                cFile.close()
            print("### Completed")
            return "Outputs", outputVocabularyFile
        elif model in ["TF-IDF", "tf-idf", "TFIDF", "tfidf", "TF", "tf"]:
            modelVocabulary = vocabCount.get_feature_names()
            print("### features")
            print(modelVocabulary)
            print("###")
            print("### matrix")
            print(countMatrix)
            print("###")
            rows, cols = countMatrix.shape
            for value in range(rows):
                for vocabIndex in range(cols):
                    listOfValues = []
                    if countMatrix[value, vocabIndex] > 0:
                        listOfValues.append(str(entities[value]))
                        listOfValues.append(str(modelVocabulary[vocabIndex]))
                        listOfValues.append(
                            str(countMatrix[value, vocabIndex]))
                        print("###")
                        print(listOfValues)
                        print("###")
                        cFile = open(os.path.join(
                            OUTPUT, outputVocabularyFile), "a+")
                        cFile.write("\t".join(listOfValues))
                        cFile.write("\n")
                        cFile.close()
            print("### Completed")
            return 'Outputs', outputVocabularyFile
    else:
        frqModel = "TFIDF"
        wordsImportance(modelFile, frqModel, fileName,
                        columnName, by, modelFileFolder, fileNameFolder)
        # wordsImportance(fileName, columnName, by, model=frqModel, modelFileFolder="Texts")


"""   
# Read CSV File
def read_csv(fileName, json_file, format):
    completeFileName = os.path.join(TEXT_FOLDER, fileName)
    outputFile = os.path.join(OUTPUT, json_file)
    csv_rows = []
    with open(completeFileName) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])
        write_json(csv_rows, outputFile, format)

# Convert csv data into json and write it
def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        if format == "pretty":
            f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
        else:
            f.write(json.dumps(data))
"""


def searchEntityInText(kgFile, kgAttrib, textFile, textAttrib, folder="Texts"):
    dfKg = readDataFile(kgFile)
    dfText = readDataFile(textFile)
    listOfKg = dfKg[kgAttrib].tolist()
    listOfText = dfText[textAttrib].tolist()
    count = 0
    setOfWords = []
    for text in listOfText:
        for word in listOfKg:
            if str(text).find(str(word)) != -1:
                setOfWords.append(str(word))
                count += 1
    print(Counter(setOfWords))
    print("Vocabulary of Kg", len(setOfWords))
    print(count)


def cleaningText(stoplist, Text):
    """
    This function removes all words present in the list called stoplist from the given Text
    Parameters:
    :param stoplist: a list of stop words 
    :param Text: a text
    return a list of word clean from stop words 
    """
    # Removing stopwords and punctuations
    sentence = [word for word in str(Text).split() if word not in stoplist]
    return sentence


def createVocabulary(stoplist, Text):
    """
    This function creates a vocabulary, given a list of stope-words and a text 
    :param stoplist: is a list of stop words
    :param Text: is a text 
    Returns the vocabulary as a list and the number of words in the vocabulary
    """
    numberOfVocab = 0
    vocab = []
    if isinstance(Text, list):
        for text in Text:
            textWord = cleaningText(stoplist, text)
            vocab += textWord
    elif isinstance(Text, str):
        textWord = cleaningText(stoplist, Text)
        vocab = textWord
    vocab = list(set(vocab))
    numberOfVocab = len(vocab)
    return vocab, numberOfVocab


"""
This function create a common vocabulary from a list of words 
stoplist: list of stop word to avoid on vocabulary retrieval
listOfFiles: file we will process to get create a common vocabulary
columnNames : is a list of colunms to focus on, for files
"""


def createCommonVocabulary(stoplist, listOfFiles, columnNames, folder):
    commonVocabulary = []
    commonVocabularySize = 0
    listOfSentence = createListOfText(listOfFiles, columnNames, folder)
    vocab, vocabSize = createVocabulary(stoplist, listOfSentence)
    commonVocabulary = vocab
    commonVocabularySize = vocabSize
    return commonVocabulary, commonVocabularySize


"""
This function takes a list of stop-words, a list of text and a window size
and creates a co-occurrence matrix of the words from the words in the list
"""


def createCooccurrenceMatrix(stoplist, listOfText, windSize=1):
    vocab, numberOfVocab = createVocabulary(stoplist, listOfText)
    print(vocab)
    print(numberOfVocab)
    cooccurenceMat = []
    for x in range(len(vocab)):
        y = x+1
        while y in range(len(vocab)):
            print(vocab[x], ' - ', vocab[y])
            row = [0]*len(vocab)
            for text in listOfText:
                text = cleaningText(stoplist, text)
                if vocab[x] in text and vocab[y] in text:
                    i = text.count(vocab[x])
                    index = text.index(vocab[x])
                    if i == 1 and index+windSize < len(text) and text[index+windSize] == vocab[y]:
                        # row = [0]*len(vocab)
                        row[y] += 1
                        print(row)
                    elif i > 1:
                        row = [0]*len(vocab)
                        for k in range(len(text)):
                            if text[k] == vocab[x] and k+windSize < len(text) and text[k+windSize] == vocab[y]:
                                row[y] += 1
                        print(row)
            y += 1
            cooccurenceMat.append(row)

    return cooccurenceMat


"""
This function finds an element is a list of list 
"""


def findElementInListOfList(listOfList, element):
    find = False
    index = 0
    while find == False and index in range(len(listOfList)):
        if element in listOfList[index]:
            find = True
        else:
            index += 1
    if index not in range(len(listOfList)):
        return False
    else:
        return True


"""
This function takes list of index of points of a cooccurence matrix
and calculate their center point 
listOfCenters: list of points indexes 
cooccurenceMat: list of vectors 
Returns the center point of the list of vectors 
"""


def calculateCenter(listOfPoints, cooccurenceMat):
    centerPoint = np.array([0]*len(cooccurenceMat[0]))
    for i in listOfPoints:
        centerPoint = centerPoint + np.array(cooccurenceMat[i])
    centerPoint = centerPoint/len(listOfPoints)
    print('Calculate center', centerPoint)
    return centerPoint


def compareSelectedVectors(firstSelectedVector, secondSelectedVector):
    """
    compareSelectedVectors returns true if the two vectors are different
    """
    if len(firstSelectedVector) == len(secondSelectedVector):
        i = 0
        difference = False
        while i in range(len(firstSelectedVector)) and difference == False:
            if len(firstSelectedVector[i]) == len(secondSelectedVector[i]):
                for j in range(len(firstSelectedVector[i])):
                    if firstSelectedVector[i][j] not in secondSelectedVector[i]:
                        difference = True
                i += 1
            else:
                difference = True
        if i not in range(len(firstSelectedVector)):
            return True
        else:
            return False
    else:
        return False


def kMeans(cooccurrenceMat, k, listOfCenters=[]):
    """
    This function takes a list a points represented as a co-occurrence matrix 
    k : number of classes 
    listOfCenters: list of centers if any 
    This function computes steps of Kmeans clustering:
    1. At the begining select centers 
    2. Do the classification of points base on centers 
    3. Compute new centers 
    Returns: selected points for various classes  and the centers
    """
    print('Cooccurrence Matrix', cooccurrenceMat)
    rows = len(cooccurrenceMat)
    # list of centers also represent the classes
    selectedVectors = []
    selectedVect = {}
    distancesFromCenters = {}
    if k <= rows:
        if not listOfCenters:
            # Initilization centre points
            i = 0
            count = 0
            while i in range(len(cooccurrenceMat)) and count != k:
                if cooccurrenceMat[i] not in listOfCenters:
                    listOfCenters.append(cooccurrenceMat[i])
                    count += 1
                i += 1
            if count < k:
                print(" Unable to have ", k, " centers")
                return [], listOfCenters

        # Classification
        for j in range(rows):
            for i in range(len(listOfCenters)):
                distancesFromCenters[i] = linalg.norm(
                    np.subtract(listOfCenters[i], cooccurrenceMat[j]))
            ind = min(distancesFromCenters,
                      key=lambda k: distancesFromCenters[k])
            selectedVect[j] = ind
        # computing centers
        listOfCenters = list()
        for j in range(k):
            v = []
            for key, val in selectedVect.items():
                if int(selectedVect[key]) == j:
                    v.append(key)
            listOfCenters.insert(j, list(calculateCenter(v, cooccurrenceMat)))
            selectedVectors.insert(j, v)
        print('New centers', listOfCenters)
    print('Selected vectors end', selectedVectors)
    return selectedVectors, listOfCenters


def completeKmeans(selectedVectors, cooccurrenceMat, k, itteration, listOfCenters=[]):
    """
    The complete  Kmeans cluster function. 
    Parameters: 
    param: selectedVectors: a list of list of vectors indexes selected for classes 
    param: cooccurenceMat: the co-occurrence matrix of vectors to classy 
    param: k: the number of classes 
    - itteration: the number of itteration to be run for the algorithm
    - listOfCenters: list of the center of each class 
    Returns: the list of selected vectors for each class 
    """
    print('Itteration', itteration)
    newSelectedVectors, newListOfCenters = kMeans(
        cooccurrenceMat, k, listOfCenters)
    if compareSelectedVectors(newSelectedVectors, selectedVectors) == False and itteration-1 > 0:
        completeKmeans(newSelectedVectors, cooccurrenceMat,
                       k, itteration-1, newListOfCenters)
    else:
        return newSelectedVectors


"""
This function task a list of text a fit a model that will be used to creat a term-document matrix.
"""


def createTfIdfAndBowModel(listOfText):
    tfIdfVectorizer = TfidfVectorizer()
    bowVectorizer = CountVectorizer(stop_words='english')
    tfIdfVectorizer.fit(listOfText)
    bowVectorizer.fit(listOfText)
    with open(os.path.join(MODEL, "tfIdfVectorizer"), "+wb") as f:
        pickle.dump(tfIdfVectorizer, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    with open(os.path.join(MODEL, "bowVectorizer"), "+wb") as f:
        pickle.dump(bowVectorizer, f, pickle.HIGHEST_PROTOCOL)
    f.close()


def generateTermDocumentMatrix(listText):
    """
    This function takes a list of text.
    It returns a matrix of term-document 
    """
    with open(os.path.join(MODEL, "tfIdfVectorizer"), "rb") as f:
        tfIdfVectorizer = pickle.load(f)
    f.close()
    X = tfIdfVectorizer.transform(listText)
    print(tfIdfVectorizer.vocabulary_)
    print("Number of words in vocabulary: ", len(tfIdfVectorizer.vocabulary_))
    print(X)
    return X


def partitionDataset(datasetFileCSV, listOfpartition, datasetFileCSVFolder):
    """
    This function create partitions of a given CSV data file
    """
    df = readDataFile(datasetFileCSV, datasetFileCSVFolder)
    rows, cols = df.shape
    initFileName = datasetFileCSV.split(".")[0]
    if isinstance(listOfpartition, int):
        fileName = initFileName+"_partition_"+str(listOfpartition)+"_"+str(
            datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"
        partitionFrame = df.iloc[0:int((listOfpartition*rows)/100)]
        df.to_csv(os.path.join(datasetFileCSVFolder, fileName),
                  sep='\t', encoding='utf-8')
        return datasetFileCSVFolder, fileName
    elif isinstance(listOfpartition, list):
        listOfFileNames = []
        listOfFileNamesFolder = []
        for part in listOfpartition:
            partitionFrame = df.iloc[0:int((part*rows)/100)]
            fileName = initFileName+"_partition_"+str(part)+"_"+str(
                datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"
            df.to_csv(os.path.join(os.path.join(DATA_FOLDER, datasetFileCSVFolder), fileName),
                      sep='\t', encoding='utf-8')
            listOfFileNames.append(fileName)
            listOfFileNamesFolder.append(datasetFileCSVFolder)
        return listOfFileNamesFolder, listOfFileNames


def dropRowsWithEmptyProperty(datasetFileCSV, datasetFileCSVFolder):
    df = readDataFile(datasetFileCSV, datasetFileCSVFolder)
    df.replace('', np.nan, inplace=True)
    df.dropna(inplace=True)
    initFileName = datasetFileCSV.split(".")[0]
    fileName = initFileName+"_clean_"+"_"+str(
        datetime.now()).replace(":", "").replace("-", "").replace(" ", "").split(".")[0]+".csv"

    df.to_csv(os.path.join(os.path.join(DATA_FOLDER, datasetFileCSVFolder), fileName),
              sep='\t', index=False, encoding='utf-8')

    return datasetFileCSVFolder, fileName
