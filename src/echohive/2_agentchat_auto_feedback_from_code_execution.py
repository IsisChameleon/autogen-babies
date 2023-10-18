import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4", "gpt-4-0314"],
    },
)

# create an AssistantAgent named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "seed": 42,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
    },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
)
# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER", #or set to "ALWAYS" to get human input every time a message is received or set to "TERMINATE" to get human input only when a termination message is received or the number of auto reply reaches the max_consecutive_auto_reply
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # set to True or image name like "python:3" to use docker
    },
)
# the assistant receives a message from the user_proxy, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""What date is today? Compare the year-to-date gain for META and TESLA.""",
)

# # followup of the previous question
user_proxy.send(
    recipient=assistant,
    message="""Plot a chart of their stock price change YTD and save the python file and save the plot to stock_price_ytd.png.""",
)

# #start a loop for a chat
# first_message = True
# while True:
#     if first_message:
#         user_input = input("Enter your message: ")
#         user_proxy.initiate_chat(
#             assistant,
#             message=f"""{user_input}""",
#         )
#         first_message = False

#     else:
#         user_input = input("Enter your message: ")
#         user_proxy.send(
#             recipient=assistant,
#             message=f"""{user_input}""",
#         )

