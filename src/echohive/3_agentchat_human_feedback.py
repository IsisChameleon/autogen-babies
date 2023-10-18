import autogen

# have this as a OAI_CONFIG_LIST.json file or have this in your environment variable
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")

# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "seed": 41,
        "config_list": config_list,
    }
)
# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
    "work_dir": "test_dir",
    "use_docker": False,  # set to True or image name like "python:3" to use docker
    },
)

# the purpose of the following line is to log the conversation history
autogen.ChatCompletion.start_logging()

math_problem_to_solve = """
Find $a + b + c$, given that $x+y \\neq -1$ and 
\\begin{align}
	ax + by + c & = x + 7,\\
	a + bx + cy & = 2x + 6y,\\
	ay + b + cx & = 4x + y.
\\end{align}.
"""

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(assistant, message=math_problem_to_solve)

import json
# save the conversation history to conversations.json
json.dump(autogen.ChatCompletion.logged_history, open("conversations.json", "w"), indent=4)