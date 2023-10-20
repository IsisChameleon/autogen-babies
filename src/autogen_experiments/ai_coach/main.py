import os
import dotenv
# import autogen
# from .modules.db import PostgresDB

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
    
    
    prompt = f"Help the human make this fitness goal S.M.A.R.T and devise a training plan: {args.prompt}."



    # build the autogen gpt_configuration object
    gpt4_config = {
        "use_cache":False,
        "temperature": 0,
        "config_list": config_list_from_models(["gpt-4"]),
        "request_timeout": 120,
        # "functions":[
        #     {
        #         "name": "run_sql",
        #         "description": "Run a SQL query against a postgres database",
        #         "parameters": {
        #             # "type": "string",
        #             # "description": "The SQL query to run",
        #             # "type": "object",
        #             # "properties": {
        #             #     "sql": {
        #             #         "type": "string",
        #             #         "description": "The SQL query to run",
        #             #     }
        #             # },
        #             # "required":["sql"],
        #         }
        #     }
        # ]
        }

        # # build the function map
        # function_map = {
        #     "run_sql": db.run_sql
        # }

    # create our terminate message function
    def is_termination_message(content):
        have_content = content.get("content", None) is not None
        if have_content and "APPROVED" in content["content"]:
            return True
        return False
    
    COMPLETION_PROMPT = "If everything looks good, respond with APPROVED"
    USER_PROXY_PROMPT = (
        "A human admin. Interact with the agents to set goals and define human training plan. Plan execution needs to be approved by this admin."
        + COMPLETION_PROMPT
    )
    PHYSICAL_TRAINER_PROMPT = (
        "Physical Trainer. You Create a tailored workout regimen based on the individual’s goals, current fitness level, and mobility assessment. Adapt the plan as per feedback from the data analyst. You don't write code."
        + COMPLETION_PROMPT
    )
    NUTRITIONIST_PROMPT =  (
        "Nutritionist. Analyze dietary habits, suggest modifications based on the individual’s goals, and monitor adherence to the dietary plan through available data. You don't write code."
        + COMPLETION_PROMPT
    )
    SPORT_PSYCHOLOGIST_PROMPT =  (
        "Sport Psychologist. You provide mental health advice and motivation.  Offer cognitive-behavioral strategies and mindfulness techniques to overcome mental barriers to training. You don't write code."
        + COMPLETION_PROMPT
    )
    DATA_SCIENTIST_PROMPT =  (
        "Data Scientist. Set up a system for tracking workouts, nutrition, and other relevant metrics, analyzing this data to suggest optimizations to the training and nutrition plans. You track and analyze fitness data. You don't write code."
        + COMPLETION_PROMPT
    )

    # Using Autogen library define a set of agents with specific roles to help to user clarify training 
    # goal and devise a very detailed day by day training plan. Assign each agent a specific duty.

    # First agent:
    # admin user proxy agent - takes in the user request and manages the group chat. It will take the user to talk
    # to all the specialists and get the final plan approved.
    user_proxy = UserProxyAgent(
        name="Admin",
        system_message=USER_PROXY_PROMPT,
        code_execution_config=False,
        human_input_mode="ALWAYS",
        is_termination_msg=is_termination_message,
    )

    # Physical trainer
    physical_trainer = AssistantAgent(
        name="Physical_Trainer",
        llm_config=gpt4_config,
        system_message=PHYSICAL_TRAINER_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
    )

    # Nutritionist
    nutritionist = AssistantAgent(
        name="Nutritionist",
        llm_config=gpt4_config,
        system_message=NUTRITIONIST_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
    )

    # Sport psychologist
    sport_psychologist = AssistantAgent(
        name="Sport_Psychologist",
        llm_config=gpt4_config,
        system_message=SPORT_PSYCHOLOGIST_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
    )

    # Data scientist to track and analyse fitness data
    data_scientist = AssistantAgent(
        name="Data_Scientist",
        llm_config=gpt4_config,
        system_message=DATA_SCIENTIST_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
    )

    # create a group chat and initiate the chat
    groupchat = GroupChat(agents=[user_proxy, physical_trainer, nutritionist, sport_psychologist, data_scientist], messages=[], max_round=10)
    manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

    user_proxy.initiate_chat(
        manager,
        clear_history=True,
        message=prompt,
    )       

if __name__ == '__main__':
    main()
