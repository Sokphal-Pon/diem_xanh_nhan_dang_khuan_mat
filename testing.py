import pyodbc
from datetime import datetime 
# Connect to SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=YOURS\HELLOSQL;DATABASE=SDdatabase;UID=sa;PWD=hello@123')
cursor = conn.cursor()

# Execute SQL query
cursor.execute("SELECT * FROM sinh_vien_info")

# Fetch a single row
student = cursor.fetchone()
print(student)


# Close connection
conn.close()