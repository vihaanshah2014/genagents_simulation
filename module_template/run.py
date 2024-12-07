#!/usr/bin/env python
import os
import json
import subprocess
from dotenv import load_dotenv
from typing import Union, Dict, Any, List
from naptha_sdk.schemas import AgentRunInput, OrchestratorRunInput, EnvironmentRunInput
from naptha_sdk.utils import get_logger
from module_template.schemas import InputSchema
from module_template.simulation_engine.global_methods import *
from module_template.genagents.genagents import GenerativeAgent

load_dotenv()

logger = get_logger(__name__)

LLM_CONFIG_PATH = "module_template/configs/llm_configs.json"

def load_llm_configs(config_path=LLM_CONFIG_PATH):
    try:
        with open(config_path, 'r') as f:
            configs = json.load(f)
        return {config['config_name']: config for config in configs}
    except FileNotFoundError:
        logger.error(f"LLM config file not found at {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM config file at {config_path}")
        return {}

class BasicModule:
    def __init__(self, module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput], llm_config_name: str):
        self.module_run = module_run
        self.llm_configs = load_llm_configs()
        if llm_config_name not in self.llm_configs:
            raise ValueError(f"LLM config '{llm_config_name}' not found in {LLM_CONFIG_PATH}")
        self.llm_config = self.llm_configs[llm_config_name]

        # Instead of relying on agent_deployment.config, we hard-code the agent folder or retrieve it from inputs/context.
        # For example, using a known folder:
        agent_folder = "module_template/agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"

        self.agent = GenerativeAgent(agent_folder)

    def func(self, conversation_history: Union[List[List[str]], str, Dict[str, Any]]):
        """
        Generate an utterance given the conversation history.
        conversation_history: [[speaker, text], ...]
        If input is not in correct format, attempt to parse/convert.
        """
        logger.info("Running func method in BasicModule")

        if isinstance(conversation_history, str):
            # Attempt to parse if it's a JSON string
            try:
                conversation_history = json.loads(conversation_history)
            except:
                conversation_history = [["User", conversation_history]]
        elif isinstance(conversation_history, dict):
            # If it's a dict, assume it may have a 'messages' key
            conversation_history = conversation_history.get("messages", [])

        if not isinstance(conversation_history, list) or not all(isinstance(i, list) and len(i) == 2 for i in conversation_history):
            conversation_history = []

        # Use the GenerativeAgent to get a response
        agent_response = self.agent.utterance(conversation_history)
        return agent_response

# Default entrypoint when the module is executed
def run(module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput], llm_config_name: str):
    basic_module = BasicModule(module_run, llm_config_name)
    method = getattr(basic_module, module_run.inputs.func_name, None)
    if method is None:
        raise ValueError(f"Method '{module_run.inputs.func_name}' not found in BasicModule")

    return method(module_run.inputs.func_input_data)

if __name__ == "__main__":
    # For local testing
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments

    naptha = Naptha()
    agent_deployments = load_agent_deployments(
        "module_template/configs/agent_deployments.json",
        load_persona_data=False,
        load_persona_schema=False,
    )

    input_params = InputSchema(func_name="func", func_input_data=[["Jane Doe", "Hello, how are you?"]])
    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0] if agent_deployments else None,
        consumer_id=naptha.user.id,
    )

    llm_config_name = "model_2"  # Example config name
    response = run(agent_run, llm_config_name)
    print("Agent response:", response)
