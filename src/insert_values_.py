from Query_ import Query
from constants import BODY, IMPORTDATA, REQUESTDATA
from utils import get_parent_tag

insertion_count = 0
current_guid = ""


def insert_in_tables(root, file_working_on, cursor, connection, default=True):
    print("Inserting Values now ... ")
    global current_guid
    if default:
        for tally_message in root[BODY][IMPORTDATA][REQUESTDATA]:
            if tally_message.tag == "TALLYMESSAGE":
                # TALLYMESSAGE will have attribute GUID, set that to global
                current_guid = tally_message.attrib["GUID"]
                for child in tally_message:
                    process_child(child, file_working_on, cursor, connection)
    else:
        process_child(root, file_working_on, cursor, connection)

    print("Inserted ", insertion_count, " queries")


def process_child(child, file_working_on, cursor, connection):
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
            insert_in_tables(field, file_working_on, cursor, connection, False)

        elif q.field_exists(fieldName):
            q.append_to_field(fieldName, fieldValue)

        else:
            q.add_field(fieldName, fieldValue)

    query = q.get_query(file_working_on)
    if query:
        insertion_count += 1
        execute_query(query, cursor, connection)


def execute_query(query, cursor, connection):
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(query)
        connection.rollback()
        print("Error executing query:", e)


def insert_in_ref_table(reference_directory, file_working_on, cursor, connection):
    for table, field in reference_directory:
        q = Query("TABLE_REFERENCES")
        q.add_field("TABLE_NAME", table)
        if field.endswith(".LIST"):
            field = field[:-5] + "LIST"
        q.add_field("FIELD_NAME", field)
        query = q.get_query(file_working_on)
        execute_query(query, cursor, connection)