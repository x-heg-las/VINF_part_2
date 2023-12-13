## This file implement Flask app searcher for github public repositories. To run this searcher an index
## must be included in index folder (zip included). 
##
## Author: Patrik Heglas

from flask import Flask, render_template, request
import lucene

import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, BooleanClause, BooleanQuery
from org.apache.lucene.store import NIOFSDirectory
from java.nio.file import Paths
import xml.etree.ElementTree as ET


app = Flask(__name__)

# Get wiki data from index based on document id
def get_info(doc_id):
    # Index directory path
    index_directory = "./index"

    index_dir = NIOFSDirectory.open(Paths.get(index_directory))

    # Create an IndexReader
    reader = DirectoryReader.open(index_dir)

    try:
        # Retrieve the document with the specified doc_id
        doc = reader.document(doc_id)

        return  doc.get("wikis")

    finally:
        # Make sure to close the reader
        reader.close()


# Function to perform a search

def perform_search(query_string, search_fields, required_fields=None, field_values=None):
    # Set the path to your Lucene index directory
    index_directory = "./index"

    # Open the index directory
    index_dir = NIOFSDirectory(Paths.get(index_directory))
    reader = DirectoryReader.open(index_dir)

    # Create an IndexSearcher
    searcher = IndexSearcher(reader)

    if len(search_fields) == 0 and required_fields is None:
        search_fields = ['readme'] #By default search in readme column

    # Create a BooleanQuery with an OR condition
    boolean_query = BooleanQuery.Builder()
    for field in search_fields:
        # to search multiple words split with ;
        query_values = query_string.split(';')
        print(query_values)
        
        for query_value in query_values:
            print(query_value)
            parser = QueryParser(field, StandardAnalyzer())
            if field_values is not None:
                query = parser.parse(field_values[field])
            else:
                query = parser.parse(query_value)

            if required_fields is not None and field in required_fields:
                boolean_query.add(query, BooleanClause.Occur.MUST)
            else:
                boolean_query.add(query, BooleanClause.Occur.SHOULD)

    # Perform the search
    top_docs = searcher.search(boolean_query.build(), 2000) 
    records = []

    # Display search results
    print("Search results:")
    for score_doc in top_docs.scoreDocs:
        doc_id = score_doc.doc
        doc = searcher.doc(doc_id)
        record = {
            "username": doc.get('username'),
            "reponame": doc.get('reponame'),
            "readme": doc.get('readme'),
            "about": doc.get('about'),
            "languages": doc.get('languages'),
            "tags": doc.get('tags'),
            #"wiki_xml": doc.get('wikis')
            "docid": doc_id
        }

        records.append(record)

    return records

# Classic search endpoint
@app.route('/', methods=['GET', 'POST'])
def index():
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()

    results = []

    if request.method == 'POST':
        print(str(request.form.getlist('field')))

        search_fields = request.form.getlist('field')
        search_query = request.form.get('search_query', '')
        # Call your search function here
        results = perform_search(search_query, search_fields)

    return render_template('index.html', results=results)


# Advanced search endpoint
@app.route('/adv', methods=['POST'])
def advanced():
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()

    results = []

    field_options = ['reponame', 'readme', 'about', 'languages', 'username']
    selected_fields = []
    requiered_fields = []

    # Check which field inputs are filled
    for field in field_options:
        if request.form.get(f'{field}_input') != '':
            selected_fields.append(field)

    # Check what fields MUST contain given query
    for field in selected_fields:
        if request.form.get(field, '') == '1':
            requiered_fields.append(field)

    print(selected_fields)
    print(requiered_fields)

    search_values = {
        'reponame': request.form.get('reponame_input', ''),
        'username': request.form.get('username_input', ''),
        'about': request.form.get('about_input', ''),
        'readme': request.form.get('readme_input', ''),
        'languages': request.form.get('languages_input', '')
    }

    print(search_values)

    results = perform_search('', selected_fields, required_fields=requiered_fields, field_values=search_values)

    return render_template('index.html', results=results)

# Show wiki info for specified repository
@app.route('/wikiinfo/<id>', methods=['GET'])
def wikiinfo(id):
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()

    print(id) 
    data = get_info(int(id))
    root = ET.fromstring(data)
    results=[]

    for page in root.findall('.//page'):
        result = {
            'url': page.find('./url').text,
            'abstract': page.find('./abstract').text,
            'title': page.find('./title').text
        }

        results.append(result)


    return render_template('wikiInfo.html', results=results)


if __name__ == '__main__':
    lucene.initVM()

    app.run(debug=True)

