from src.constants import *
from src.main import get_tree

inner_tags = {}

def get_tags_in_tallymessage(root):
    for child in root[BODY][IMPORTDATA][REQUESTDATA]:
        if child.tag == "TALLYMESSAGE":
            inner_tag = child[0]
            inner_tag_name = inner_tag
            if inner_tag.tag not in inner_tags:
                inner_tags[inner_tag.tag] = 1
            else:
                inner_tags[inner_tag.tag] += 1    

if __name__ == "__main__":
    root = get_tree("Master.xml")
    get_tags_in_tallymessage(root)
    print(inner_tags)