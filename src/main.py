import xml.etree.ElementTree as ET
from constants import *
from utils import *
from format_ import *
from input_ import *
from database_ import create_database, get_connection, python_to_sql_types
from Query import Query

file_working_on = ""
insertion_count = 0
current_guid = ""
tables_directory = {
    # tableName: { fieldName1: type, fieldName2: type, ... }
}
reference_directory = set()
queries = []

create_database()
connection = get_connection()
cursor = connection.cursor()


def create_table(table_name, fields, prefix):
    if table_name == "GROUP":
        table_name = "TBLGROUP"
    if table_name.endswith("LIST"):
        table_name = table_name[:-5] + "LIST"
    query = f"CREATE TABLE {prefix + table_name} ("
    for field, t in fields.items():
        query += f"{field} {python_to_sql_types[t]}, "
    query = query[:-2] + ")"
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(query)
        connection.rollback()
        print("Error creating table:", e)
    

def create_tables(root, prefix):
    count = 0
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                add_table_in_dir(table_tag)

    for table_tag in tables_directory:
        fields = tables_directory[table_tag]
        if len(fields) == 0:
            continue
        create_table(table_tag, fields, prefix)
        count += 1
    print("Created ", count, " Tables")


def add_table_in_dir(table_tag):
    global tables_directory
    tableName = get_parent_tag(table_tag)

    if tableName not in tables_directory:
        tables_directory[tableName] = {}

    if tableName.endswith("LIST"):
        tables_directory[tableName]["GUID"] = type("GUID")

    for fieldA in table_tag.attrib:
        fieldAName = fieldA + "_ATTRIB"
        if fieldAName not in tables_directory[tableName]:
            tables_directory[tableName][fieldAName] = type(table_tag.attrib[fieldA])

    for field in table_tag:
        fieldName = field.tag.strip()
        fieldValue = field.text
        if fieldName.endswith(".LIST"):
            reference_directory.add((tableName, fieldName))
            add_table_in_dir(field)
        if (
            not fieldName.endswith(".LIST")
            and fieldName not in tables_directory[tableName]
        ):
            tables_directory[tableName][fieldName] = type(fieldValue)


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
        fieldName = fieldA + "_ATTRIB"
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


def create_and_insert_references(prefix=""):
    # create table with twofields "TABLE_"
    create_table("TABLE_REFERENCES", {"TABLE_NAME": str, "FIELD_NAME": str}, prefix)
    for table, field in reference_directory:
        q = Query("TABLE_REFERENCES")
        q.add_field("TABLE_NAME", table)
        if field.endswith(".LIST"):
            field = field[:-5] + "LIST"
        q.add_field("FIELD_NAME", field)
        query = q.get_query(file_working_on)
        execute_query(query)


if __name__ == "__main__":
    ask_for_config()

    # assign GUID to each TALLYMESSAGE tag
    apply_xslt(input_path_m, GUID_ADD_XSLT, MASTER_XML_OUTPUT)
    apply_xslt(input_path_t, GUID_ADD_XSLT, TRANSC_XML_OUTPUT)

    # do you want to remove weird characters?
    clean_files = input("Do you want to remove weird characters? (y/n) ")
    if clean_files.lower() == "y":
        remove_weird_characters(MASTER_XML_OUTPUT)
        remove_weird_characters(TRANSC_XML_OUTPUT)


    files = [MASTER_XML_OUTPUT, TRANSC_XML_OUTPUT]
    prefix = ["MAST", "TRAN"]

    for i in range(2):
        file_ = files[i]
        prefix_ = prefix[i]

        tables_directory = {}
        reference_directory = set()

        file_working_on = prefix_
        root = get_tree(file_)

        print("Creating Tables....")
        create_tables(root, prefix_)
        print("Inserting Values....")
        insert_in_tables(root)
        print("Inserted ", insertion_count, " queries")
        create_and_insert_references(prefix_)
        print("Created References")

    connection.close()
