import xml.etree.ElementTree as ET
import pyodbc


def get_tree(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    return root


def connect_to_database():
    connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password, autocommit=True)
    cursor = connection.cursor()
    return [connection, cursor]


def get_parent_tag(elm):
    elm_tag = elm.tag

    if elm_tag == "GROUP":
        elm_tag = "TBLGROUP"
    return elm_tag.strip()


def create_database(cursor):
    cursor.execute("CREATE DATABASE " + DATABASE_NAME)



