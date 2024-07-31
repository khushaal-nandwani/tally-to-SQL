import pyodbc

# MS SQL Server Configuration
server = "CAPSTONE\RADIX"
master_database = "master"
username = "sa"
password = "dotnet@123"

# The name of the database you want your tally data to be in
target_database = "TallyData2"

python_to_sql_types = {
    str: "NVARCHAR(MAX)",
    type(None): "NVARCHAR(MAX)",
    int: "INTEGER",
    float: "REAL",
    bool: "BOOLEAN",
    bytes: "BLOB",
}


def create_database():
    connection = pyodbc.connect(
        "DRIVER={SQL Server}"
        + ";SERVER="
        + server
        + ";DATABASE="
        + master_database
        + ";UID="
        + username
        + ";PWD="
        + password,
        autocommit=True,
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE " + target_database)
    connection.commit()


def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server}"
        + ";SERVER="
        + server
        + ";DATABASE="
        + target_database
        + ";UID="
        + username
        + ";PWD="
        + password,
        autocommit=True,
    )

def set_target_database(db_name):
    global target_database
    target_database = db_name
    
