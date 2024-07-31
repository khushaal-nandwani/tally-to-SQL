from database_ import set_target_database

input_path_m = "..\data\Master.xml"
input_path_t = "..\data\Transactions.xml"

GUID_ADD_XSLT = "..\data\guid_add.xsl"
MASTER_XML_OUTPUT = "M.xml"
TRANSC_XML_OUTPUT = "T.xml"

def ask_for_config():
    configuration_required = input("Do you want to enter configuration? (y/n) ")
    if configuration_required.lower() == "y":
        _ask_for_inputs()
    else:
        print("Using default configuration.")


def _ask_for_inputs():
    global input_path_m
    global input_path_t

    input_path_m = input("Enter path to Master's XML file: ")
    input_path_t = input("Enter path to Transactions' XML file: ")

# TODO
def _ask_for_target_database():
    db_name = input("Name the database you want to create for your Tally Data: ")
    set_target_database(db_name)