## This file contains code snipped for joining multiple XML files with same
## format into one file, with one root XML element. This was used after wikipedia
## paralel processing. This snipped was run in jupyter notebook.

import os
import xml.etree.ElementTree as ET

def merge_xml_files(input_folder, output_file):
    merged_root = ET.Element("root")

    for filename in os.listdir(input_folder):
        if filename.startswith("part"):
            filepath = os.path.join(input_folder, filename)

            # Parse the XML file
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Append the content of the current XML file to the merged XML
            merged_root.extend(root)

    # Create a new tree with the merged root
    merged_tree = ET.ElementTree(merged_root)

    # Write the merged XML to the output file
    merged_tree.write(output_file, encoding="utf-8", xml_declaration=True)

collected_files_directory = "./parsed_wiki/" # folder returned by Apache Spark containing multiple XML files to join
merged_output_file = "./merged_output2.xml" # output folder

# Merge the collected XML files
merge_xml_files(collected_files_directory, merged_output_file)

