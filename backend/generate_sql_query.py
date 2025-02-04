import torch
import duckdb
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
import os

load_dotenv()
model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
DB_PATH = os.getenv("DUCKDB_PATH")

# Load model & tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

# Function to generate SQL query using the model
def generate_sql(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=100)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Extract SQL query from the response (basic cleaning)
    sql_start = response.find("```sql")
    sql_end = response.find("```", sql_start + 1)

    if sql_start != -1 and sql_end != -1:
        sql_query = response[sql_start + 6:sql_end].strip()  # Extract SQL between ```sql and ```
    else:
        sql_query = response.strip()  # If no markdown formatting, return as is

    return sql_query.replace("\n", " ")

# Function to execute SQL query in DuckDB
def run_query(sql_query):
    # create a connection to file
    con = duckdb.connect(DB_PATH)
    try:
        result = con.execute(sql_query).fetchall()
        con.close()
        return result
    except Exception as e:
        con.close()
        return f"Error: {e}"


# Prompt the LLM to generate a SQL query
prompt = "Write a SQL query to find the top 3 most expensive transactions from a table named 'transactions'. The 'transactions' table has the following columns: date timestamp, details TEXT, amount FLOAT, category TEXT"
sql_query = generate_sql(prompt)
print(f"Generated SQL Query:\n{sql_query}")

# Run the SQL query in DuckDB
result = run_query(sql_query)
print("Query Result:")
print(result)