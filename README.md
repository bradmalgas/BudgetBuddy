# BudgetBuddy LLM Query System

## Overview

BudgetBuddy is a chatbot-powered financial assistant that allows users to query their transaction data using natural language. The system leverages a locally hosted LLM (DeepSeek Coder 1.3B) to generate SQL queries, which are executed on a DuckDB database.

## Features

- Conversational interface for querying transaction data
- LLM-generated SQL queries for DuckDB
- FastAPI-based backend API
- Locally hosted inference for cost efficiency

## Tech Stack

- **LLM**: DeepSeek Coder 1.3B Instruct
- **Database**: DuckDB
- **Backend**: FastAPI (Python)

## Setup Instructions

### Prerequisites

- Python 3.10+
- `pip` for package management
- PyTorch installed with CPU support (or GPU if available)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bradmalgas/BudgetBuddy
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download and set up the LLM:
   ```bash
   python download_llm_model.py
   ```

### Running the API

1. Start FastAPI:
   ```bash
   uvicorn generate_sql_query:app --reload
   ```
2. Test the API locally:
   Open a browser and visit `http://127.0.0.1:8000/docs` to access the interactive API documentation.

## Example Query

**User Input:**

```json
{
  "question": "What were my top 3 most expensive transactions?"
}
```

**Output:**

```json
{
  "response": [
    ["2025-02-01T10:20:00", "Details", 13748, "Category"],
    ["2024-12-01T12:09:00", "Details", 12394.2001953125, "Category"],
    ["2024-11-29T05:30:00", "Details", 9999, "Category"]
  ]
}
```

## Next Steps

- Custom Analytics & Trend Detection: Python logic that processes and summarizes query results, identifying trends, anomalies, and spending patterns.
- LLM-Powered Natural Language Responses: A second LLM (preferably small and efficient) that converts raw insights into human-friendly advice.
