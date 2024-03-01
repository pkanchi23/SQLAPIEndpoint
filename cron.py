# Streamlit user interface
import sqlite3
import pandas as pd
import os
from pathlib import Path
import openai
import promptlayer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
#uncomment to run locally
# PROMPTLAYER_API_KEY = os.environ.get('PROMPTLAYER_API_KEY')
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
promptlayer.api_key = PROMPTLAYER_API_KEY
openai.api_key = OPENAI_API_KEY
promptlayer.openai.api_key = OPENAI_API_KEY

#Connect to SQL database
current_dir = Path(__file__).parent
db_path = current_dir / 'northwind.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Function to generate a natural language question (placeholder for your logic)
def generate_natural_language_question(columns):
    # question = "How many different ship names are there?"
    variables = {
        "columns": columns
    }
    generate_question_template = promptlayer.templates.get("generate_SQL_question", {
        "provider": "openai",
        "input_variables": variables
    })

    response, pl_id = promptlayer.openai.ChatCompletion.create(
        **generate_question_template["llm_kwargs"],
        return_pl_id=True
    )
    
    # Associate request to Prompt Template
    promptlayer.track.prompt(request_id=pl_id, 
        prompt_name='NL_to_SQL', prompt_input_variables=variables)
    
    question = response.choices[0].message.content
    return question

# Function to refine SQL query using PromptLayer
def refine_sql_with_promptlayer(natural_language, columns):
    variables = {
    'columns':columns,
    'User_NL': natural_language
    }

    NL_to_SQL_template = promptlayer.templates.get("NL_to_SQL", {
        "provider": "openai",
        "input_variables": variables
    })          
    
    response, pl_id = promptlayer.openai.ChatCompletion.create(
        **NL_to_SQL_template["llm_kwargs"],
        return_pl_id=True
    )
    
    # Associate request to Prompt Template
    promptlayer.track.prompt(request_id=pl_id, 
        prompt_name='NL_to_SQL', prompt_input_variables=variables)

    refined_sql = response.choices[0].message.content
    return refined_sql, pl_id

#convert the SQL response to a natural language answer
def sql_to_NL_answer(df, natural_language):
    df = df.to_string()
    variables = {
    'data':df,
    'question': natural_language
    }

    SQL_to_NL_template = promptlayer.templates.get("SQL to NL", {
        "provider": "openai",
        "input_variables": variables
    })          
    
    response, pl_id = promptlayer.openai.ChatCompletion.create(
        **SQL_to_NL_template["llm_kwargs"],
        return_pl_id=True
    )
    
    # Associate request to Prompt Template
    promptlayer.track.prompt(request_id=pl_id, 
        prompt_name='SQL to NL', prompt_input_variables=variables)

    NL_answer = response.choices[0].message.content
    return NL_answer, pl_id

# Main
def main():
    
    # Get details of the 'Orders' table for column names
    cursor.execute("PRAGMA table_info(Orders)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Pull the first row of data for examples to pass the prompt
    cursor.execute("SELECT * FROM Orders LIMIT 1")
    example_data = cursor.fetchone()
    column_data_pairs = [f"{column_names[i]}: {example_data[i]}" for i in range(len(column_names))]
    column_data_string = "\n".join(column_data_pairs)
    
    #create a new question to ask 
    natural_language_question = generate_natural_language_question(column_data_string)

    # Generate SQL Query from natural language question
    sql_query, pl_id = refine_sql_with_promptlayer(natural_language_question, column_data_string)
    
    # Execute the SQL query
    df = pd.read_sql_query(sql_query, conn)

    # Convert the SQL query result into a natural language answer
    NL_answer, _ = sql_to_NL_answer(df, natural_language_question)

    # Output the result (for logging or further processing)
    print(NL_answer)

# Close the database connection
def close_connection():
    conn.close()

if __name__ == '__main__':
    main()
    close_connection()