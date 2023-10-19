import os
from .modules.db import PostgresDB
import dotenv

dotenv.load_dotenv()
assert os.environ.get('DATABASE_URL'), 'DATABASE_URL not found in .env file'
assert os.environ.get('OPENAI_API_KEY'), 'OPENAI_API_KEY not found in .env file'

DATABASE_URL = os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

import argparse
from .modules.llm import add_cap_ref, prompt

def main():
    # parse prompt using arg parse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI.")
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a prompt.")
        return

    # connect to db using with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DATABASE_URL)

        # call db_manager.get_table_definition_for_prompt() to get tables in prompt ready form
        table_definitions = db.get_table_definition_for_prompt()

        # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli
        prompt_with_ref = add_cap_ref(args.prompt, "Here are the table definitions:", "TABLE_DEFINITIONS", table_definitions)
        prompt_with_ref = add_cap_ref(prompt_with_ref, "Please provide the SQL query using delimiter '------------'.", "SQL_QUERY:", "")
        print('prompt_with_ref:',prompt_with_ref)

        # call llm.prompt to get a prompt_response variable
        prompt_response = prompt(prompt_with_ref)
        print('prompt_response:',prompt_response)

        # parse sql response from prompt_response using SQL_QUERY_DELIMITER '------------'
        sql_query = prompt_response.split('------------')[1].strip()
        print("sql_query:" + sql_query)

        # call db_manager.run_sql() with the parsed sql
        print("-------- POSTGRES DATA ANALYTICS AI AGENT RESPONSE --------")
        result = db.run_sql(sql_query)
        print(result)

if __name__ == '__main__':
    main()
