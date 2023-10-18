import autogen
import subprocess

config_list = autogen.config_list_from_models(model_list=["gpt-4", "gpt-3.5-turbo"])

llm_config = {
    "functions": [
        {
            "name": "python",
            "description": "run code in python and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cell": {
                        "type": "string",
                        "description": "Valid Python cell to execute.",
                    }
                },
                "required": ["cell"],
            },
        },
        {
            "name": "sh",
            "description": "run a shell script and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Valid shell script to execute.",
                    }
                },
                "required": ["script"],
            },
        },
    ],
    "config_list": config_list,
    "request_timeout": 120,
}

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding", "use_docker": True},
)

# Updated Functions
def exec_python(cell):
    local_vars = {}
    try:
        exec(cell, globals(), local_vars)
        return str(local_vars)
    except Exception as e:
        return str(e)

def exec_sh(script):
    try:
        result = subprocess.run(script, shell=True, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

# register the functions
user_proxy.register_function(
    function_map={
        "python": exec_python,
        "sh": exec_sh,
    }
)

# start the conversation
user_proxy.initiate_chat(
    chatbot,
    message="use Matplotlib to Draw two agents chatting with each other with an example dialog. save the plot to a file too.",
)