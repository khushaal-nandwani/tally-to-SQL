import xml.etree.ElementTree as ET


def get_tree(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    return root


def get_parent_tag(elm):
    elm_tag = elm.tag

    if elm_tag == "GROUP":
        elm_tag = "TBLGROUP"
    return elm_tag.strip()


def field_name(name: str):
    if name.endswith("LIST"):
        return name[:-4] + "LIST"
    return name