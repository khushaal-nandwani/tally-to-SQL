import xml.etree.ElementTree as ET
from constants import *
import sqlite3
import pyodbc
from utils import *
from format import *

file_working_on = ""
EXCLUDE_TABLES = []
SQL_KEYWORDS = ["GROUP", "USER", "ORDER", "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TABLE", "VIEW", "DATABASE", "PROCEDURE", "FUNCTION", "TRIGGER", "INDEX", "CONSTRAINT", "PRIMARY", "FOREIGN", "KEY", "CHECK", "UNIQUE", "DEFAULT", "NULL", "NOT", "AND", "OR", "IN", "BETWEEN", "LIKE", "IS", "EXISTS", "ALL", "ANY", "SOME", "CASE", "WHEN", "THEN", "ELSE", "END", "AS", "BEGIN", "COMMIT", "ROLLBACK", "TRAN", "DECLARE", "SET", "IF", "ELSE", "WHILE", "GOTO", "RETURN", "BREAK", "CONTINUE", "PRINT", "EXEC", "WITH", "GRANT", "REVOKE", "DENY", "AUTHORIZATION", "ON", "TO", "GO"]

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

insertion_count = 0
current_guid = ""
tables_directory = {
    # tableName: { fieldName1: type, fieldName2: type, ... }
}

# set of tupes
referenced_out = set()

queries = []


def create_table(table_name, fields):
    if table_name == "GROUP":
        table_name = "TBLGROUP"
    query = f"CREATE TABLE {table_name} ("
    for field, t in fields.items():
        query += f"{field} {python_to_sql_types[t]}, "
    query = query[:-2] + ")"
    cursor.execute(query)
    connection.commit()


def add_table_in_dir(table_tag):
    global tables_directory
    global reference_directory
    tableName = get_parent_tag(table_tag)

    if tableName in EXCLUDE_TABLES:
        return
    
    if tableName not in tables_directory:
        tables_directory[tableName] = {}
    
    if tableName.endswith("LIST"):
        tables_directory[tableName]["GUID"] = type("GUID")

    for fieldA in table_tag.attrib:
        fieldAName = fieldA + '_ATTRIB'
        if fieldAName not in tables_directory[tableName]:
            tables_directory[tableName][fieldAName] = type(table_tag.attrib[fieldA])

    for field in table_tag:
        fieldName = field.tag.strip()
        fieldValue = field.text
        if fieldName.endswith(".LIST"):
            referenced_out.add((tableName, fieldName))
            add_table_in_dir(field)
        if not fieldName.endswith(".LIST") and fieldName not in tables_directory[tableName]:
            tables_directory[tableName][fieldName] = type(fieldValue)


def create_tables(root):
    count = 0
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                add_table_in_dir(table_tag)
    
    for table_tag in tables_directory:
        fields = tables_directory[table_tag]
        if len(fields) == 0:
            continue
        create_table(table_tag, fields)
        count += 1
    print("Created ", count, " Tables")


def insert_in_tables(root, default=True):
    global current_guid
    if default:
        for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
            if tally_message.tag == "TALLYMESSAGE":
                # TALLYMESSAGE will have attribute GUID, set that to global
                current_guid = tally_message.attrib["GUID"]
                for child in tally_message:
                    process_child(child)
    else:
        process_child(root)


def process_child(child):
    global insertion_count
    global current_guid

    parentName = get_parent_tag(child)
    q = Query(parentName)

    if parentName.endswith("LIST"):
        q.add_field("GUID", current_guid)

    for fieldA in child.attrib:
        fieldName = fieldA + '_ATTRIB'
        fieldValue = child.attrib[fieldA]
        if fieldA == "REMOTEID":
            current_guid = fieldValue
        q.add_field(fieldName, fieldValue)

    for field in child:
        fieldName = field.tag
        fieldValue = field.text
                
        if fieldName == "GUID":
            current_guid = fieldValue
                    
        if fieldName.endswith("LIST"):
            insert_in_tables(field, False)

        elif q.field_exists(fieldName):
            q.append_to_field(fieldName, fieldValue)

        else:
            q.add_field(fieldName, fieldValue)
                

    query = q.get_query(file_working_on)
    if query:
        insertion_count += 1
        execute_query(query)


def execute_query(query):
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(query)
        connection.rollback()
        print("Error executing query:", e)


def print_xml_structure(element, level=0):
    indent = "  " * level
    print(f"{indent}<{element.tag}>")
    for child in element:
        print_xml_structure(child, level + 1)
    print(f"{indent}</{element.tag}>")


def create_and_insert_references():
    # create table with twofields "TABLE_"
    create_table("TABLE_REFERENCES", {"TABLE_NAME": str, "FIELD_NAME": str})
    for table, field in referenced_out:
        q = Query("TABLE_REFERENCES")
        q.add_field("TABLE_NAME", table)
        if field.endswith(".LIST"):
            field = field[:-5] + "LIST"
        q.add_field("FIELD_NAME", field)
        query = q.get_query(file_working_on)
        execute_query(query)


if __name__ == "__main__":
    input_path_1 = "..\data\Master4.xml"
    input_path_2 = "..\data\Transactions4.xml"
    XSLT_PATH = "..\data\guid_add.xsl"
    output_path_1 = "M.xml"
    output_path_2 = "T.xml"

    # remove_weird_characters(input_path_1)
    # remove_weird_characters(input_path_2)
    apply_xslt(input_path_1, XSLT_PATH, output_path_1)
    apply_xslt(input_path_2, XSLT_PATH, output_path_2)

    files_to_convert = {
        output_path_1: 'MAST',
        output_path_2: 'TRAN'
    }

    for file_, prefix_ in files_to_convert.items():
        tables_directory = {}
        referenced_out = set()
        file_working_on = prefix_
        root = get_tree(file_)


        print("Creating Tables....")
        create_tables(root)
        print("Inserting Values....")
        insert_in_tables(root)
        print("Inserted ", insertion_count, " queries")
        create_and_insert_references()
        print("Created References")

    
    connection.close()

