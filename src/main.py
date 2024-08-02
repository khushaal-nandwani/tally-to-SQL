from constants import *
from create_tables_ import create_ref_table, create_tables
from insert_values_ import insert_in_ref_table, insert_in_tables
from utils import *
from format_ import *
from target_files import *
from database_ import create_database, drop_database

file_working_on = ""
tables_directory = {
    # tableName: { fieldName1: type, fieldName2: type, ... }
}
reference_directory = set()


if __name__ == "__main__":
    ask_for_config()

    drop_database()
    connection, cursor = create_database()

    clean_files = input("Do you want to remove weird characters? (y/n) ")
    if clean_files.lower() == "y":
        remove_weird_characters(MASTER_XML_OUTPUT)
        remove_weird_characters(TRANSC_XML_OUTPUT)

    apply_xslt(input_path_m, GUID_ADD_XSLT, MASTER_XML_OUTPUT)
    apply_xslt(input_path_t, GUID_ADD_XSLT, TRANSC_XML_OUTPUT)

    files = [MASTER_XML_OUTPUT, TRANSC_XML_OUTPUT]
    prefix = ["MAST", "TRAN"]  # or prefices?

    for i in range(len(files)):
        file_ = files[i]
        prefix_ = prefix[i]

        tables_directory = {}
        reference_directory = set()

        file_working_on = prefix_
        root = get_tree(file_)

        create_tables(
            root, prefix_, connection, cursor, reference_directory, tables_directory
        )
        print("Inserting Values now ... ")
        count = insert_in_tables(root, file_working_on, cursor, connection, True)
        print("Inserted ", count, " queries")

        create_ref_table(prefix_, connection, cursor)
        insert_in_ref_table(reference_directory, file_working_on, cursor, connection)
    print("\nTally to SQL successful. Thank you:)\nFor queries contact @github.com/khushaal-nandwani")

    connection.close()
