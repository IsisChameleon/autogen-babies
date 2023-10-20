import os
import dotenv
import autogen
from .modules.db import PostgresDB

from autogen.agentchat import GroupChatManager, UserProxyAgent, AssistantAgent, GroupChat
from autogen.oai import config_list_from_models


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
        prompt = add_cap_ref(prompt, "Here are the table definitions:", "TABLE_DEFINITIONS", table_definitions)

        # build the autogen gpt_configuration object
        gpt4_config = {
            "use_cache":False,
            "temperature": 0,
            "config_list": config_list_from_models(["gpt-4"]),
            "request_timeout": 120,
            "functions":[
                {
                    "name": "run_sql",
                    "description": "Run a SQL query against a postgres database",
                    "parameters": {
                        # "type": "string",
                        # "description": "The SQL query to run",
                        # "type": "object",
                        # "properties": {
                        #     "sql": {
                        #         "type": "string",
                        #         "description": "The SQL query to run",
                        #     }
                        # },
                        # "required":["sql"],
                    }
                }
            ]
        }

        # build the function map
        function_map = {
            "run_sql": db.run_sql
        }

        # create our terminate message function
        def is_termination_message(content):
            have_content = content.get("content", None) is not None
            if have_content and "APPROVED" in content["content"]:
                return True
            return False
        
        COMPLETION_PROMPT = "If everything looks good, respond with APPROVED"
        USER_PROXY_PROMPT = (
            "A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin."
            + COMPLETION_PROMPT
        )
        DATA_ENGINEER_PROMPT = (
            """Data Engineer. You follow an approved plan. You write SQL queries to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try."""
            + COMPLETION_PROMPT
        )
        DATA_ANALYST_PROMPT = (
            """Data Analyst. You follow an approved plan. You execute SQL queries and analyze the results. You don't write code."""
            + COMPLETION_PROMPT
        )
        PRODUCT_MANAGER_PROMPT = (
            """Product Manager. Validate the response to make sure it's correct. Provide feedback to the team and guide the project direction."""
            + COMPLETION_PROMPT
        )

        # create a set of agents with specific roles
        # admin user proxy agent - takes in the prompt and manages the group chat
        user_proxy = UserProxyAgent(
            name="Admin",
            system_message=USER_PROXY_PROMPT,
            code_execution_config=False,
            human_input_mode="NEVER",
            is_termination_msg=is_termination_message,
        )

        # data engineer agent - generates the sql query
        data_engineer = AssistantAgent(
            name="Data_Engineer",
            llm_config=gpt4_config,
            system_message=DATA_ENGINEER_PROMPT,
            code_execution_config=False,
            human_input_mode="NEVER",
            is_termination_msg=is_termination_message,
        )

        # sr data analyst agent - run the sql query and generates the response
        data_analyst = AssistantAgent(
            name="Data_Analyst",
            llm_config=gpt4_config,
            system_message=DATA_ANALYST_PROMPT,
            code_execution_config=False,
            human_input_mode="NEVER",
            is_termination_msg=is_termination_message,
            function_map=function_map
        )

        # product manager - validate the response to make sure it's correct
        product_manager = AssistantAgent(
            name="Product_Manager",
            system_message=PRODUCT_MANAGER_PROMPT,
            code_execution_config=False,
            llm_config=gpt4_config,
            human_input_mode="NEVER",
            is_termination_msg=is_termination_message,
        )

        # create a group chat and initiate the chat
        groupchat = GroupChat(agents=[user_proxy, data_engineer, data_analyst, product_manager], messages=[], max_round=10)
        manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

        user_proxy.initiate_chat(
            manager,
            clear_history=True,
            message=prompt,
        )
        

if __name__ == '__main__':
    main()
