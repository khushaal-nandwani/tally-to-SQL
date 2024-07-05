import xml.etree.ElementTree as ET
from constants import *
import sqlite3

connection = sqlite3.connect('tally.db')
cursor = connection.cursor()

python_to_sql_types = {
    str: "TEXT",
    type(None): "TEXT",
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
    print(query)
    cursor.execute(query)
    connection.commit()


def get_tree(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    return root

tables = {
    # tableName: { field1: type, field2: type, ... }
}


def create_tables(root):
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_name in tally_message:
                if table_name not in tables:
                    tables[table_name.tag] = {}
                    for field in table_name:
                        if field.tag.endswith(".LIST"):
                            field.tag = field.tag[:-5] + "XLIST"
                        if field.tag not in tables[table_name.tag]:
                            tables[table_name.tag][field.tag] = type(field.text)
                # table name in table
                else:
                    print("WE ARE HEREEEE\n\n")
                    for field in table_name:
                        if field.tag not in tables[table_name.tag]:
                            print("NOT FOUND ADDING\n\n\n")
                            tables[table_name.tag][field.tag] = type(field.text)

    
    # create tables
    for table_name in tables:
        create_table(table_name, tables[table_name])



def insert_in_tables(root):
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_name in tally_message:
                if table_name == "GROUP":
                    table_name = "TBLGROUP"
                fields = tables[table_name.tag]
                query = f"INSERT INTO {table_name.tag} ("
                for field in table_name:
                    query += f"{field.tag}, "
                query = query[:-2] + ") VALUES ("
                for field in table_name:
                    query += f"'{field.text}', "
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


