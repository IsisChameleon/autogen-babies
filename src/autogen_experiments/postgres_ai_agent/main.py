import os
from .modules.db import PostgresDB
import dotenv

dotenv.load_dotenv()
assert os.environ.get('DATABASE_URL'), 'DATABASE_URL not found in .env file'
assert os.environ.get('OPENAI_API_KEY'), 'OPENAI_API_KEY not found in .env file'

DATABASE_URL = os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def main():
    # parse prompt using arg parse

    # connect to db using with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DATABASE_URL)
        db.upsert("goals", {"id": 1, "goal_description": "fist goal"})
        print(db.get("goals", 1))


    # call db_manager.get_table_definition_for_prompt() to get tables in prompt ready form

    # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli

    # call llm.prompt to get a prompt_response variable

    # parse sql response from prompt_response using SQL_QUERY_DELIMITER '------------'

    # call db_manager.run_sql() with the parsed sql

if __name__ == '__main__':
    main()