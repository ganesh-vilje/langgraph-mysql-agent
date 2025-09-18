import os
import mysql.connector
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

def run_query(query: str):
    """Run a raw SQL query and return rows + columns."""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    cursor.close()
    conn.close()
    return rows, columns

@tool
def query_mysql(query: str):
    """Execute a SQL query on the MySQL database and return results as structured JSON-like data."""
    try:
        rows, columns = run_query(query)
        if not rows:
            return {"results": []}
        return {"results": [dict(zip(columns, row)) for row in rows]}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_schema():
    """Return the database schema: tables and their columns."""
    try:
        schema_info = {}
        rows, _ = run_query(
            f"""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{MYSQL_CONFIG['database']}'
            ORDER BY table_name, ordinal_position;
            """
        )
        for table, column, dtype in rows:
            if table not in schema_info:
                schema_info[table] = []
            schema_info[table].append({"column": column, "type": dtype})
        return {"schema": schema_info}
    except Exception as e:
        return {"error": f"Error fetching schema: {e}"}
