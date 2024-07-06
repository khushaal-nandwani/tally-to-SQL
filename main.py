import xml.etree.ElementTree as ET
from constants import *
import sqlite3
import pyodbc
import re

XMLFILE = 'Master2.xml'
DATABASE_NAME = "TallyData"
EXCLUDE_TABLES = ['INCOMETAXCLASSIFICATION', 'INCOMETAXSLAB']

server = 'CAPSTONE\RADIX' 
database = 'master'  # Connect to the master database to create a new database
username = 'sa' 
password = 'dotnet@123'

connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password, autocommit=True)
cursor = connection.cursor()

cursor.execute("CREATE DATABASE " + DATABASE_NAME)
connection.commit()

database = DATABASE_NAME
connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = connection.cursor()

python_to_sql_types = {
    str: "NVARCHAR(MAX)",
    type(None): "NVARCHAR(MAX)",
    int: "INTEGER",
    float: "REAL",
    bool: "BOOLEAN",
    bytes: "BLOB"
}

# create a function to create table, the function can take parameters, table name and a list of fields
def create_table(table_name, fields):
    if table_name == "GROUP":
        table_name = "TBLGROUP"
    query = f"CREATE TABLE {table_name} ("
    for field, t in fields.items():
        query += f"{field} {python_to_sql_types[t]}, "
    query = query[:-2] + ")"
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(e)
        # if e[0] == '42S01':
        #     print("Table already exists, skipping", table_name)
    

def get_tree(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    return root

tables = {
    # tableName: { fieldName1: type, fieldName2: type, ... }
}

def create_tables(root):
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                tableName = table_tag.tag
                if tableName in EXCLUDE_TABLES:
                    continue
                if tableName == "GROUP":
                    tableName = "TBLGROUP"
                if tableName not in tables:
                    tables[tableName] = {}
                for field in table_tag:
                    fieldName = field.tag
                    fieldValue = field.text
                    if fieldName.endswith(".LIST"):
                        fieldName = fieldName[:-5] + "XLIST"
                    if fieldName not in tables[tableName]:
                        tables[tableName][fieldName] = type(fieldValue)
                        
                for field_attrib in table_tag.attrib:
                    field_attrib_name = field_attrib + '_ATTRIB'
                    if field_attrib_name not in tables[tableName]:
                        tables[tableName][field_attrib_name] = type(table_tag.attrib[field_attrib])
        
    for table_tag in tables:
        create_table(table_tag, tables[table_tag])

def _get_table_name(table_tag):
    tableName = table_tag.tag
    if tableName == "GROUP":
        tableName = "TBLGROUP"
    return tableName

def _get_field_name(field):
    fieldName = field.tag
    if fieldName.endswith(".LIST"):
        fieldName = fieldName[:-5] + "XLIST"
    return fieldName

def insert_in_tables(root):
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                tableName = _get_table_name(table_tag)
                if tableName in EXCLUDE_TABLES:
                    continue
                fields = tables[tableName]
                query = f"INSERT INTO {tableName} ("
                for field in table_tag:
                    fieldName = _get_field_name(field)
                    fieldValue = field.text
                    query += f"{fieldName}, "
                for field_attrib in table_tag.attrib:
                    field_attrib = field_attrib + '_ATTRIB'
                    query += f"{field_attrib}, "
                query = query[:-2] + ") VALUES ("
                for field in table_tag:
                    fieldValue = field.text
                    # if fieldvalue has ' , replace it with ''
                    fieldName = field.tag
                    if fieldName.endswith(".LIST"):
                        # concat all the field values
                        for subfield in field:
                            fieldValue += f"{subfield.tag}: {subfield.text}:: "
                    if fieldValue is None:
                        fieldValue = ""
                    fieldValue = fieldValue.replace('\n', ' ').replace('\r', ' ')
                    fieldValue = re.sub(r'\s{2,}', ' ', fieldValue)
                    if fieldValue is not None:
                        fieldValue = fieldValue.replace("'", "''")
                    query += f"'{fieldValue}', "
                for field_attrib in table_tag.attrib:
                    fieldValue = table_tag.attrib[field_attrib]
                    if fieldValue is None:
                        fieldValue = ""
                    else:
                        fieldValue = fieldValue.replace("'", "''")
                    query += f"'{table_tag.attrib[field_attrib]}', "
                query = query[:-2] + ")"
                print(query)
                cursor.execute(query)
                connection.commit()
        
if __name__ == "__main__":
    root = get_tree(XMLFILE)
    create_tables(root)
    insert_in_tables(root)


