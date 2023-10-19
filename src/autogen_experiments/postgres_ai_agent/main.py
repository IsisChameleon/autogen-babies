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
    
    prompt = f"Fulfill this database query: {args.prompt}."

    # connect to db using with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DATABASE_URL)

        # call db_manager.get_table_definition_for_prompt() to get tables in prompt ready form
        table_definitions = db.get_table_definition_for_prompt()

        # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli
        prompt_with_ref = add_cap_ref(prompt, "Here are the table definitions:", "TABLE_DEFINITIONS", table_definitions)

        # build the autogen gpt_configuration object

        # build the function map

        # create our terminate message function

        # create a set of agents with specific roles
            # admin user proxy agent - takes in the prompt and manages the group chat
            # data engineer agent - generates the sql query
            # sr data analyst agent - run the sql query and generates the response
            # product manager - validate the response to make sure it's correct

        # create a group chat and initiate the chat
        

if __name__ == '__main__':
    main()
