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
        gpt_config = {
            "seed": 42,
            "temperature": 0,
            "request_timeout": 120,
        }

        # build the function map
        # Not applicable in this context

        # create our terminate message function
        # Not applicable in this context

        # create a set of agents with specific roles
        # admin user proxy agent - takes in the prompt and manages the group chat
        user_proxy = autogen.UserProxyAgent(
            name="Admin",
            system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
            code_execution_config=False,
        )

        # data engineer agent - generates the sql query
        data_engineer = autogen.AssistantAgent(
            name="Data Engineer",
            llm_config=gpt_config,
            system_message='''Data Engineer. You follow an approved plan. You write SQL queries to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
        ''',
        )

        # sr data analyst agent - run the sql query and generates the response
        data_analyst = autogen.AssistantAgent(
            name="Data Analyst",
            llm_config=gpt_config,
            system_message='''Data Analyst. You follow an approved plan. You execute SQL queries and analyze the results. You don't write code.'''
        )

        # product manager - validate the response to make sure it's correct
        product_manager = autogen.AssistantAgent(
            name="Product Manager",
            system_message='''Product Manager. Validate the response to make sure it's correct. Provide feedback to the team and guide the project direction.''',
            llm_config=gpt_config,
        )

        # create a group chat and initiate the chat
        groupchat = autogen.GroupChat(agents=[user_proxy, data_engineer, data_analyst, product_manager], messages=[], max_round=50)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt_config)

        user_proxy.initiate_chat(
            manager,
            message=f"{args.prompt}",
        )
        

if __name__ == '__main__':
    main()
