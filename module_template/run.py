#!/usr/bin/env python
import os
import json
import subprocess
from dotenv import load_dotenv
from naptha_sdk.schemas import AgentRunInput, OrchestratorRunInput, EnvironmentRunInput
from naptha_sdk.utils import get_logger
from module_template.schemas import InputSchema
from module_template.simulation_engine.global_methods import *
from module_template.genagents.genagents import GenerativeAgent
from typing import Union

load_dotenv()

logger = get_logger(__name__)


class Conversation:
    def __init__(self, agent_folder, interviewer_name="Interviewer"):
        # Load the agent from the specified folder
        self.agent = GenerativeAgent(agent_folder)
        self.interviewer_name = interviewer_name
        self.conversation_history = []

    def start(self):
        print(f"Starting conversation with {self.agent.get_fullname()}.\nType 'exit' to end the conversation.\n")
        while True:
            # Get input from the interviewer
            user_input = input(f"{self.interviewer_name}: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Conversation ended.")
                break
            # Add the interviewer's utterance to the conversation history
            self.conversation_history.append([self.interviewer_name, user_input])
            # Get the agent's response
            agent_response = self.agent.utterance(self.conversation_history)
            print(f"{self.agent.get_fullname()}: {agent_response}")
            # Add the agent's response to the conversation history
            self.conversation_history.append([self.agent.get_fullname(), agent_response])

#TODO add run function


# Example usage:
if __name__ == "__main__":
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments

    # Initialize naptha client
    naptha = Naptha()

    # We'll just use the same input schema stub
    input_params = InputSchema(func_name="func", func_input_data="")

    # Load agent deployments (if needed)
    agent_deployments = load_agent_deployments(
        "module_template/configs/agent_deployments.json",
        load_persona_data=False,
        load_persona_schema=False,
    )

    # For demonstration purposes, we pick the first deployment if it exists
    agent_deployment = agent_deployments[0] if len(agent_deployments) > 0 else None

    # Create a dummy AgentRunInput (this is how we "use naptha the way the second one does")
    # We do not necessarily need to use it directly in the conversation logic, 
    # but this shows that we are integrating the naptha environment setup.
    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployment,
        consumer_id=naptha.user.id,
    )

    # Specify the folder where the agent is stored
    agent_folder = "module_template/agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"

    # Create a Conversation instance
    conversation = Conversation(agent_folder, interviewer_name="Jane Doe")
    # Start the conversation
    conversation.start()
