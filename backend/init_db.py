import duckdb
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DUCKDB_PATH")
CSV_FILE = os.getenv("CSV_PATH")

# Create a connection to file
con = duckdb.connect(DB_PATH)

# Create a table in database file (note: column types can be automatically detected but results may vary based on input)
con.sql("""
    CREATE TABLE IF NOT EXISTS transactions (
        date timestamp,
        details TEXT,
        amount FLOAT,
        category TEXT,
    );
""")

insertDataIntoTableSQLStatement = f"INSERT INTO transactions SELECT * FROM read_csv('{CSV_FILE}')"

# Read data from csv file
con.sql(insertDataIntoTableSQLStatement)

# Query the table
con.table("transactions").show()


# Count the number of transactions:
numTransactionsQuery = con.sql("SELECT COUNT(*) FROM transactions;")
print("Count the number of transactions:")
print(numTransactionsQuery)

# Find the most recent transaction:
recentTransactionsQuery = con.sql("SELECT * FROM transactions ORDER BY date DESC LIMIT 1;")
print("Find the most recent transaction:")
print(recentTransactionsQuery)

# Find the top 3 biggest expenses:
query = con.sql("SELECT * FROM transactions ORDER BY amount DESC LIMIT 3;")
print("Find the top 3 biggest expenses:")
print(query)

# Explicitly close the connection
con.close()
