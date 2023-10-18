import autogen

# We will use docker for this example. Make sure to set use_docker to True if you want to use docker in UserProxyAgent.

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

# this is where you can set openai api configurations such as temperature, top_p, etc.
llm_config={
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
)
# you will be prompted to provide feedback after the assistant agent sends a "TERMINATE" signal in the end of the message. If you don't provide any feedback (by pressing Enter directly), the conversation will finish. Before the "TERMINATE" signal, the user proxy agent will try to execute the code suggested by the assistant agent on behalf of the user.
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    # Make sure to set use_docker to True if you want to use docker. if not specified, it will use the default value True.
    code_execution_config={"work_dir": "web", "use_docker":True},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
Who should read this paper: https://arxiv.org/abs/2308.08155
""",
)