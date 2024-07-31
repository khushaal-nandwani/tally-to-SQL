import os
from lxml import etree

def apply_xslt(xml_path, xslt_path, output_path):
    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass

    xml_tree = etree.parse(xml_path)
    xslt_tree = etree.parse(xslt_path)

    transform = etree.XSLT(xslt_tree)
    transformed_tree = transform(xml_tree)

    transformed_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

REMOVE_CHARS = ["", "&#4; "]

def remove_weird_characters(file_path):
    with open(file_path, 'r') as file:
        filedata = file.read().splitlines()
        for char in REMOVE_CHARS:
            filedata = filedata.replace(char, "")
    with open(file_path, 'w') as file:
        file.write(filedata)

