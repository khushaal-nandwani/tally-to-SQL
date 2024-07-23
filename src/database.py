# MS SQL Server Configuration
server = 'CAPSTONE\RADIX' 
database = 'master' 
username = 'sa' 
password = 'dotnet@123'

# The name of the databse you want your tally data to be in 
DATABASE_NAME = "TallyData"

python_to_sql_types = {
    str: "NVARCHAR(MAX)",
    type(None): "NVARCHAR(MAX)",
    int: "INTEGER",
    float: "REAL",
    bool: "BOOLEAN",
    bytes: "BLOB"
}
