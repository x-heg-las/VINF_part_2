## This program represents indexer for github repository entities.
## To run this script you need to install lucence (tested on version 9.7.0) and requirements. Sample data is provided.
## To run: python3 indexer.py
##
## Author: Patrik Heglas

import lucene
import argparse
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import NIOFSDirectory
from java.nio.file import Paths
import xml.etree.ElementTree as ET


lucene.initVM()


# Initialize the Lucene index
index_directory = "./index"
analyzer = StandardAnalyzer()
config = IndexWriterConfig(analyzer)
index_dir = NIOFSDirectory(Paths.get(index_directory))
writer = IndexWriter(index_dir, config)

parser = argparse.ArgumentParser()
parser.add_argument('--data-path', help='Filepath to data to index', default='data.xml')
args = parser.parse_args()

# Path to the XML file
xml_file_path = args.data_path

# Parse XML and index documents
tree = ET.parse(xml_file_path)
root = tree.getroot()

for doc_elem in root.findall('repository'):
    reponame = doc_elem.find('reponame').text
    readme = doc_elem.find('readme').text
    username = doc_elem.find('username').text
    about = doc_elem.find('about').text or ''
    tags = doc_elem.find('tags').text or ''
    languages = doc_elem.find('languages').text or ''
    wikis = ET.tostring(doc_elem.find('wikis')) or ''
    

    # Create Lucene Document
    doc = Document()
    doc.add(Field("reponame", reponame, TextField.TYPE_STORED))
    doc.add(Field("readme", readme, TextField.TYPE_STORED))
    doc.add(Field("about", about, TextField.TYPE_STORED))
    doc.add(Field("languages", languages, TextField.TYPE_STORED))
    doc.add(Field("tags", tags, TextField.TYPE_STORED))
    doc.add(Field("wikis", wikis, TextField.TYPE_STORED))
    doc.add(Field("username", username, TextField.TYPE_STORED))
    

    # Add the document to the Lucene index
    writer.addDocument(doc)

# Commit and close the Lucene index writer
writer.commit()
writer.close()
