from constants import BODY, IMPORTDATA, REQUESTDATA
from utils import get_parent_tag
from database_  import python_to_sql_types


def create_table(table_name, fields, prefix, connection, cursor):
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


def create_tables(root, prefix, connection, cursor, reference_directory, tables_directory):
    print("Creating Tables with prefix", prefix, "...")
    count = 0
    for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
        if tally_message.tag == "TALLYMESSAGE":
            for table_tag in tally_message:
                _add_table_in_dir(table_tag, reference_directory, tables_directory)

    for table_tag in tables_directory:
        fields = tables_directory[table_tag]
        if len(fields) == 0:
            continue
        create_table(table_tag, fields, prefix, connection, cursor)
        count += 1
    print("Created ", count, " Tables")


def _add_table_in_dir(table_tag, reference_directory, tables_directory):
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
            _add_table_in_dir(field, reference_directory, tables_directory)
        if (
            not fieldName.endswith(".LIST")
            and fieldName not in tables_directory[tableName]
        ):
            tables_directory[tableName][fieldName] = type(fieldValue)


def create_ref_table(prefix, connection, cursor):
    print("Creating References...")
    create_table("TABLE_REFERENCES", {"TABLE_NAME": str, "FIELD_NAME": str}, prefix, connection, cursor)