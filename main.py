import xml.etree.ElementTree as ET
from constants import *
import sqlite3
import pyodbc

XMLFILE = 'Master.xml'

server = 'CAPSTONE\RADIX' 
database = 'master'  # Connect to the master database to create a new database
username = 'sa' 
password = 'dotnet@123'

connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password, autocommit=True)
cursor = connection.cursor()

cursor.execute("CREATE DATABASE TallyData")
connection.commit()

database = 'TallyData' 
connection = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = connection.cursor()

python_to_sql_types = {
    str: "NVARCHAR(50)",
    type(None): "NVARCHAR(50)",
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
    cursor.execute(query)
    connection.commit()

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
                    if field_attrib not in tables[tableName]:
                        tables[tableName][field_attrib] = type(table_tag.attrib[field_attrib])
        
    for table_tag in tables:
        create_table(table_tag, tables[table_tag])


def insert_in_tables(root):
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                tableName = table_tag.tag
                if tableName == "GROUP":
                    tableName = "TBLGROUP"
                fields = tables[tableName]
                query = f"INSERT INTO {tableName} ("
                for field in table_tag:
                    fieldName = field.tag
                    fieldValue = field.text
                    if fieldName.endswith(".LIST"):
                        fieldName = fieldName[:-5] + "XLIST"
                    query += f"{fieldName}, "
                for field_attrib in table_tag.attrib:
                    query += f"{field_attrib}, "
                query = query[:-2] + ") VALUES ("
                for field in table_tag:
                    fieldValue = field.text
                    fieldName = field.tag
                    if fieldName.endswith(".LIST"):
                        # concat all the field values
                        for subfield in field:
                            fieldValue += f"{subfield.tag}: {subfield.text}:: "
                    query += f"'{fieldValue}', "
                for field_attrib in table_tag.attrib:
                    query += f"'{table_tag.attrib[field_attrib]}', "
                query = query[:-2] + ")"
                cursor.execute(query)
                connection.commit()
        
        
def insert_dict_in_txt(dictionary):
    """ Creates a new file with the dictionary values cleanly printed """
    with open("output.txt", "w") as f:
        for key in dictionary:
            f.write(f"{key}: {dictionary[key]}\n")
        f.write("\n")


if __name__ == "__main__":
    root = get_tree("Master.xml")
    create_tables(root)
    insert_in_tables(root)


