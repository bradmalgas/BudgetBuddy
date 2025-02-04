import torch
import duckdb
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()
load_dotenv()
model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
DB_PATH = os.getenv("DUCKDB_PATH")

# Load model & tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

# Function to generate SQL query using the model
def generate_sql(prompt: str) -> str:
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
def run_query(sql_query: str):
    # create a connection to file
    con = duckdb.connect(DB_PATH)
    try:
        result = con.execute(sql_query).fetchall()
        con.close()
        return result
    except Exception as e:
        con.close()
        raise HTTPException(status_code=400, detail=f"Query Execution Error: {str(e)}")
    
class QueryRequest(BaseModel):
    question: str

# Health check
@app.get("/")
def read_root():
    return {"message": "BudgetBuddy API is running"}

# Generate and execute SQL query based on user input
@app.post("/query")
def get_transactions_by_category(request: QueryRequest):
    prompt = f"""You are an expert DuckDB SQL assistant. Generate a correct DuckDB SQL query for the given request.
    ### Table Schema:
    - **transactions** (date TIMESTAMP, details TEXT, amount FLOAT, category TEXT)
    ### Example 1
    Question: What were my 3 biggest expenses?
    SQL: SELECT * FROM transactions ORDER BY amount DESC LIMIT 3;
    ### Example 2
    Question: How much did I spend on groceries last month?
    SQL: SELECT SUM(amount) FROM transactions WHERE category ILIKE '%grocery%' AND date >= DATE_TRUNC('month', CURRENT_DATE);
    ### Example 3
    Question: What was my largest transaction in the last two weeks?
    SQL: SELECT * FROM transactions WHERE date >= CURRENT_DATE - INTERVAL '14 days' ORDER BY amount DESC LIMIT 1;
    ### Example 4
    Question: How much have I spent on fast food?
    SQL: SELECT SUM(amount) FROM transactions WHERE category ILIKE '%fast food%';
    ### Example 5
    Question: How much did I spend on Uber this month?
    SQL: SELECT SUM(amount) FROM transactions WHERE details ILIKE '%uber%' AND date >= DATE_TRUNC('month', CURRENT_DATE);
    ### Example 6
    Question: Have I bought anything from PlayStation?
    SQL: SELECT * FROM transactions WHERE details ILIKE '%playstation%';
    ### Example 7
    Question: What have I bought from KFC?
    SQL: SELECT details, SUM(amount) FROM transactions WHERE details ILIKE '%kfc%' GROUP BY details;
    ### New Query
    Question: {request.question}
    SQL:
    ```"""
    sqlQuery = generate_sql(prompt)
    results = run_query(sqlQuery)

    return {"response": results}
    
    # # Debugging mode:
    # return {"prompt": prompt, "sql": sqlQuery, "result": results}