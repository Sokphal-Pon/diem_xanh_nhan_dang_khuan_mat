import pyodbc
#import numpy as np

# Connect to SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=YOURS\HELLOSQL;DATABASE=SDdatabase;UID=sa;PWD=hello@123')
cursor = conn.cursor()

# Execute SQL query
cursor.execute("SELECT * FROM sinh_vien_info")

# Fetch data
students = cursor.fetchall()

for student in students:
    print(student)

# Close connection
conn.close()