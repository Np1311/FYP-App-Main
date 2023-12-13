import sqlite3
from django.conf import settings
from django.db import connection
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Get the database configuration from Django settings

# Connect to the SQLite database
conn = sqlite3.connect('fyp')
cursor = conn.cursor()

# Get a list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the list of tables
if tables:
    print("Tables in the database:")
    for table in tables:
        print(table[0])
else:
    print("No tables found in the database.")

# Close the connection
conn.close()
