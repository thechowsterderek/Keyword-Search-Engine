
from __future__ import print_function
import glob
import collections
import re
from bs4 import BeautifulSoup
import json
import sys
import math

# Number of Documents
global N
N = 1001

# Posting class
# An object that contains docId, term frequency, and posting score
class Posting:
    score = 0
    def __init__(self, docId, tf):
        self.docId = docId
        self.tf = tf
    def toString(self):
        return "docId: " + str(self.docId) + "\t tf: " + str(self.tf) + "\t score: " +str(self.score)

# get_json_data
# gets_json_data from bookkeeping.json
def get_json_data():
    json_file = open('bookkeeping.json')
    json_str = json_file.read()
    json_data = json.loads(json_str)
    json_file.close()
    return json_data

# getTermDict
# Generates a termDict (term->freq) from tokens
def getTermDict(tokens):
    termDict = {}
    for i in tokens:
        strippedText = re.sub('[^a-zA-Z0-9 ]', ' ', i.text)
        text = strippedText.lower().strip().split()
        for term in text:
            if( termDict.get(term.strip()) == None ):
                termDict[term.strip()] = 1
            else:
                termDict[term.strip()] += 1
    return termDict

# populateIndex
# Populate index using the passed in parameters
def populateIndex(index, termDict, filePath):
    for key in termDict:
        if(index.get(key) == None):
            index[key] = [Posting(filePath, termDict[key])]
        else:
            index[key].append(Posting(filePath, termDict[key]))
    return index

# indexer
# Updates champ_index and main_index with contents of the file in filePath
def indexer(filePath, main_index, champ_index):
    f = open(filePath)
    soup = BeautifulSoup(f, "html.parser")
    champTokens = soup.find_all(["b", "h1", "h2", "h3"])
    tokens = soup.find_all()
    
    #Populate main_index
    termDict = getTermDict(tokens)
    main_index = populateIndex(main_index, termDict, filePath)
    
    #Populate champ_index
    champTermDict = getTermDict(champTokens)
    champ_index = populateIndex(champ_index, champTermDict, filePath)
    
    f.close()
    return main_index, champ_index

# printIndex
# Prints the contents of the index passed in
def printIndex(index):
    for key in index:
        print("Term: " + key + "\t", end='')
        for posting in index[key]:
            print(posting.toString())
        print()

# printIndexInfo
# Prints information related to the index
def printIndexInfo(index):
    print(str("# of Docs") + str("# of Unique Terms").rjust(25) + str("Size of Index (KB)").rjust(25))
    print(str(N) + str(len(index.keys())).rjust(25) + str(sys.getsizeof(index)/1024).rjust(25))


# main_tf_idf
# Calculates tf-idf score for main index
def main_tf_idf(index):
    for key in index:
        for posting in index[key]:
            posting.score = math.log((1+posting.tf), 2.0) * math.log((N/len(index[key])), 2.0)
    return index

# champ_tf_idf
# Calculates tf-idf score for champ index
def champ_tf_idf(index):
    for key in index:
        for posting in index[key]:
            posting.score = math.log((1+posting.tf), 2.0) * math.log((N/len(index[key])), 2.0)
            posting.score *= 100
    return index

# get_query
# Gets query from user
def get_query():
    user_input = raw_input('What would you like to search: ')
    user_input = re.sub('[^a-zA-Z0-9 ]', ' ', user_input)
    return user_input.lower().strip()

# update_query_results
# Updates queryResuls with newer scores
def update_query_results(index, word, queryResults):
    if(index.get(word) != None):
        for posting in index.get(word):
            if(queryResults.get(posting.docId) == None):
                queryResults[posting.docId] = posting.score
            else:
                queryResults[posting.docId] += posting.score
    return queryResults

# handle_query
# Handles query entered by user by getting a list of results
# sorted by tf_idf score in descending order
def handle_query(query,cIndex,mIndex):
    words = []
    queryResults = {}
    words = query.split(" ")
    for word in words:
        queryResults = update_query_results(mIndex, word.strip(), queryResults)
        queryResults = update_query_results(cIndex, word.strip(), queryResults)
    return sorted(queryResults, key=queryResults.get, reverse=True)

# print_results_helper
# Allows user to view next or previous pages of results, if available
def print_results_helper(results, urlMap, limit, offset):
    if(len(results) > (offset + limit) and offset >= limit):
        user_input = raw_input('Type [N] to view the next page of results or [P] to view the previous page of results: ')
        user_input = user_input.lower()
        if(user_input == 'n'):
            print_results(results, urlMap, limit, (offset + limit))
        elif(user_input == 'p'):
            print_results(results, urlMap, limit, (offset - limit))

    elif(offset >= limit):
        user_input = raw_input('Type [P] to view the previous page of results: ')
        user_input = user_input.lower()
        if(user_input == 'p'):
            print_results(results, urlMap, limit, (offset - limit))

    elif(len(results) > (offset + limit)):
        user_input = raw_input('Type [N] to view the next page of results: ')
        user_input = user_input.lower()
        if(user_input == 'n'):
            print_results(results, urlMap, limit, (offset + limit))

# print_results
# Prints results of user query
def print_results(results, urlMap, limit = 5, offset = 0):
    page = (offset + limit)/limit
    result_count = 0
    
    if(len(results) == 0):
        print("No match found.")
        return
    
    print("")
    if(offset == 0):
        print(str(len(results)) + " Hits")
    
    while(len(results) > (offset + result_count) and result_count < limit):
        print(str(offset+result_count+1) + ")" + urlMap[results[offset+result_count]])
        print("")
        result_count += 1
    
    print("Page (" + str(page) + ")")
    print_results_helper(results, urlMap, limit, offset)

# print_menu
# Prints main menu
def print_menu():
    print("Main Menu")
    print("Please select one of the following options: ")
    print("1) Print index info")
    print("2) Search")
    print("3) Exit program")
    option = raw_input('Enter option: ')
    return option

# build_indexes
# Builds main and champ indexes
def build_indexes():
    main_index = {}
    champ_index = {}
    
    paths = ["0/[0-9]*",
             "1/[0-9]*",
             "2/[0-9]*"]
    for path in paths:
        files = glob.glob(path)
        for f in files:
            main_index, champ_index = indexer(f, main_index, champ_index)

    main_index = main_tf_idf(main_index)
    champ_index = champ_tf_idf(champ_index)
    return main_index, champ_index

# main
if __name__ == "__main__":
    main_index, champ_index = build_indexes()
    urlMap = get_json_data()
    option = print_menu()
    
    while(option != '3'):
        if(option == '1'):
            print("Important words index info: ")
            printIndexInfo(champ_index)
            print("All other words index info: ")
            printIndexInfo(main_index)
            print("")
            option = print_menu()
        
        elif(option == '2'):
            user_input = get_query()
            results = handle_query(user_input, champ_index, main_index);
            print_results(results, urlMap)
            print("")
            option = print_menu()
        
        else:
            print("Invalid Input!")
            option = raw_input("Please enter an appropriate option: ")
