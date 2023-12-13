## This program, using Apache Spark, parses wikipedia data based on provided keywords programming_languages
## retrieved from github repository crawl. If wikipedia title contains at least one of provided keyfords, we want to save its
## abstract. This script was run on Spark version 3.5.0. To run this script you need to have wiki-data xml file included with --wiki-data attribute.
## Sample file wikidata.xml is already provided. Run with:  spark-submit --packages com.databricks:spark-xml_2.12:0.17.0 --master local wikidata.py --wiki-data wikidata.xml 
##
## Author: Patrik Heglas

from pyspark.sql import SparkSession
from pyspark.sql.types import  BooleanType
import re
import argparse
from pyspark.sql.functions import expr, lit, col, udf, max, any_value

# Keywords to filter wikipedia titles
programming_languages = {
        'NSIS', 'Inno', 'PLpgSQL', 'Sass', 'CMake', 'Smalltalk', 'Meson', 'HCL', 'Smarty', 'Classic',
        'Roff', 'Vala', 'Java', 'C#', 'MDX', 'AppleScript', 'Procfile', 'jq', 'Blade', 'Astro', 'AspectJ',
        'Racket', 'CoffeeScript', 'TSQL', 'Q#', 'MLIR', 'Handlebars', 'HTML', 'PowerShell', 'Agda', 'Fluent',
        'C++', 'QMake', 'WebAssembly', 'Hack', 'HiveQL', 'Groovy', 'Objective-C', 'Twig', 'WebIDL', 'OCaml',
        'Dart', 'DTrace', 'C', 'Cuda', 'Python', 'ReScript', 'Go', 'Solidity', 'Scala', 'Standard', 'CSS',
        'Lua', 'Pug', 'Stylus', 'SCSS', 'OpenSCAD', 'Rust', 'Dockerfile', 'Swift', 'LLVM', 'Typst', 'Xtend',
        'Elixir', 'ShaderLab', 'Mako', 'Haml', 'MoonScript', 'D', 'Batchfile', 'XSLT', 'Terra', 'Kotlin',
        'Clojure', 'GLSL', 'V', 'Makefile', 'F#', 'ASL', 'Starlark', 'Metal', 'Vim', 'HLSL', 'SWIG', 'MATLAB',
        'Pawn', 'JavaScript', 'Julia', 'ApacheConf', 'Vue', 'Shell', 'Markdown', 'Jupyter', 'Assembly', "Cap'n",
        'Lex', 'XS', 'M4', 'Perl', 'Factor', 'Jinja', 'Common', 'Svelte', 'Emacs', 'Nginx', 'Objective-C++',
        'ASP.NET', 'OpenQASM', 'POV-Ray', 'Prolog', 'Sage', 'Ruby', 'R', 'PHP', 'Nix', 'TypeScript', 'WGSL',
        'TeX', 'Cython', 'ANTLR', 'Fortran', 'CUE', 'Haskell', 'Less', 'Gherkin', 'Xonsh', 'Rich', 'Mustache',
        'FreeMarker', 'Processing', 'Nunjucks', 'PLSQL', 'Yacc', 'Bicep', 'EJS'
    }

# Filter condition to pick suitable wiki data
def filter_repos(column):

    # check if keyword is present in title
    if any(f' {query} ' in column for query in programming_languages):
        return True
   
    return False

if __name__ == '__main__':
    spark = SparkSession.builder.appName('DataJoiner').getOrCreate()

    parser = argparse.ArgumentParser()
    parser.add_argument('--wiki-data', help='Wikipedia XML file', default='wikidata.xml')
    parser.add_argument('--wiki-root', help='Root tag of wiki xml', default='feed')
    parser.add_argument('--wiki-row', help='Row tag of wiki xml', default='doc')

    args = parser.parse_args()

    wiki_root = args.wiki_root
    wiki_row = args.wiki_row
    wiki_data_file_path = args.wiki_data
   
    wiki_data = spark.read.format('xml').options(rootTag=wiki_root, rowTag=wiki_row).load(wiki_data_file_path)

    print(wiki_data.count())

    # DEBUG: print schema
    wiki_data.printSchema()

    custom_filter_udf = udf(filter_repos, BooleanType())

    # filtering of rows
    filtered_data = wiki_data.filter(custom_filter_udf('title'))

    filtered_data.show()
    print(filtered_data.count())

    # Save filtered data to file(s)
    filtered_data.select("*").write.format("com.databricks.spark.xml") \
    .option("wikis", "Wiki") \
    .option("page", "Page") \
    .save('filtered-wikis')

    spark.stop()
   

