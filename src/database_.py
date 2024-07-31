import pyodbc

# MS SQL Server Configuration
server = "CAPSTONE\RADIX"
master_database = "master"
username = "sa"
password = "dotnet@123"

# The name of the database you want your tally data to be in
target_database = "TestData"

python_to_sql_types = {
    str: "NVARCHAR(MAX)",
    type(None): "NVARCHAR(MAX)",
    int: "INTEGER",
    float: "REAL",
    bool: "BOOLEAN",
    bytes: "BLOB",
}


def create_database():
    connection, cursor = _get_master_db()
    cursor.execute("CREATE DATABASE " + target_database)
    connection.commit()
    print("Creating database: " + target_database)
    return _get_connection_to_target()


def _get_connection_to_target():
    connection = pyodbc.connect(
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
    return connection, connection.cursor()


def set_target_database(db_name):
    global target_database
    target_database = db_name


def drop_database():
    connection, cursor = _get_master_db()
    cursor.execute("SELECT name FROM master.dbo.sysdatabases")
    databases = cursor.fetchall()
    databases = [x[0] for x in databases]
    if target_database in databases:
        resp = input("Target Database already exists. Would you like to drop it? (y/n) ")
        if resp.lower() == "y":
            cursor.execute("DROP DATABASE " + target_database)
            connection.commit()
        else:
            print("Exiting.")
            exit(0)
    else:
        print("Database does not exist. Creating a new one.")


def _get_master_db():
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
    return connection, cursor


if __name__ == "__main__":
    drop_database()
        