from lxml import etree


def apply_xslt(xml_path, xslt_path, output_path):
    # Load the XML file
    xml_tree = etree.parse(xml_path)

    # Load the XSLT file
    xslt_tree = etree.parse(xslt_path)

    # Create an XSLT transformer
    transform = etree.XSLT(xslt_tree)

    # Transform the XML
    transformed_tree = transform(xml_tree)

    # Write the output to a new XML file
    transformed_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')



# Scans through the whole xml file, and replaces "" with ""  
def remove_weird_characters(file_path):
    with open(file_path, 'r') as file:
        filedata = file.read()
        filedata = filedata.replace("", "")
    with open(file_path, 'w') as file:
        file.write(filedata)

