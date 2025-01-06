#!/usr/bin/env python
import argparse
import os
import json
import random
from typing import List, Dict

from dotenv import load_dotenv
from naptha_sdk.schemas import AgentRunInput, AgentDeployment
from naptha_sdk.utils import get_logger
from genagents_simulation.schemas import InputSchema
from naptha_sdk.client.naptha import Naptha
from genagents_simulation.genagents.genagents import GenerativeAgent

load_dotenv()

logger = get_logger(__name__)

LLM_CONFIG_PATH = "genagents_simulation/configs/llm_configs.json"

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
    def __init__(self, module_run: AgentRunInput):
        self.module_run = module_run
        self.llm_configs = load_llm_configs()
        
        # Extract LLM config name and agent count
        llm_config_name = module_run.inputs.llm_config_name
        if not llm_config_name:
            raise ValueError("Missing 'llm_config_name' in input parameters.")
        if llm_config_name not in self.llm_configs:
            raise ValueError(f"LLM config '{llm_config_name}' not found in {LLM_CONFIG_PATH}")
        self.llm_config = self.llm_configs[llm_config_name]

        agent_count = module_run.inputs.agent_count

        # Base paths for agents
        gss_base_path = os.path.join(os.path.dirname(__file__), "agent_bank/populations/gss_agents")
        single_agent_path = os.path.join(os.path.dirname(__file__), "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae")
        self.agents = []

        # Initialize agents based on count or percentage
        all_gss_agents = self._get_agent_folders(gss_base_path)
        if isinstance(agent_count, int):
            if agent_count == 1:
                selected_agents = [single_agent_path]
            else:
                selected_agents = random.sample(all_gss_agents, min(agent_count, len(all_gss_agents)))
        else:
            # Handle percentage-based agent_count if needed in the future
            percentage = int(agent_count.rstrip('%'))
            num_agents = max(1, int(len(all_gss_agents) * percentage / 100))
            selected_agents = random.sample(all_gss_agents, num_agents)

        for agent_path in selected_agents:
            try:
                agent = GenerativeAgent(agent_path)
                self.agents.append(agent)
            except Exception as e:
                logger.error(f"Failed to load agent: {str(e)}")

    def _get_agent_folders(self, base_path: str) -> List[str]:
        try:
            agent_folders = []
            for root, dirs, files in os.walk(base_path):
                if 'scratch.json' in files and 'meta.json' in files:
                    agent_folders.append(root)
            return sorted(agent_folders)
        except Exception as e:
            logger.error(f"Error accessing agent folders: {str(e)}")
            return []

    def func(self, input_data: Dict[str, List[str]]):
        logger.info(f"Running module function with {len(self.agents)} agents")
        logger.debug(f"Input data received: {input_data}")

        # Validate input_data format
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary with questions as keys and lists of options as values.")

        for question, options in input_data.items():
            if not isinstance(options, list):
                raise ValueError(f"Expected a list of options for question '{question}', but got {type(options).__name__}.")

        all_responses = []
        response_counts = {}
        explanations = {}

        for question, options in input_data.items():
            response_counts[question] = {}
            explanations[question] = []
            for option in options:
                response_counts[question][option] = 0

        for agent in self.agents:
            agent_response = agent.categorical_resp(input_data)
            all_responses.append(agent_response)

            for q_idx, question in enumerate(input_data):
                response = agent_response['responses'][q_idx]
                reasoning = agent_response['reasonings'][q_idx]
                response_counts[question][response] += 1
                explanations[question].append(reasoning)

        visual_summary = {}
        for question in input_data:
            total = sum(response_counts[question].values())
            visual_summary[question] = {
                'counts': response_counts[question],
                'percentages': {option: f"{(count / total * 100):.1f}%" for option, count in response_counts[question].items()},
                'visual': {option: f"{'█' * int(count / total * 20)} {count}/{total}" for option, count in response_counts[question].items()},
                'explanations': explanations[question],
            }

        return {
            "individual_responses": all_responses,
            "summary": visual_summary,
            "num_agents": len(self.agents),
        }

def run(module_run: AgentRunInput):
    basic_module = BasicModule(module_run)
    method = getattr(basic_module, module_run.inputs.func_name, None)
    if method is None:
        raise ValueError(f"Method '{module_run.inputs.func_name}' not found in BasicModule")
    return method(module_run.inputs.func_input_data)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run agent simulations with custom questions and options.')
    parser.add_argument('--question', type=str, required=True, help='The question to ask the agents.')
    parser.add_argument('--options', type=str, required=True, help='Comma-separated options for the question (e.g., "Yes,No,Undecided").')
    parser.add_argument('--llm_config_name', type=str, default='model_2', help='The LLM configuration name to use.')
    parser.add_argument('--agent_count', type=int, default=1, help='The number of agents to simulate.')

    return parser.parse_args()

if __name__ == "__main__":
    naptha = Naptha()

    # Load agent deployments and parse into AgentDeployment instances
    deployment_config_path = "genagents_simulation/configs/deployment.json"
    try:
        with open(deployment_config_path, "r") as f:
            deployment_config_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Deployment config file not found at {deployment_config_path}")
        raise

    # Convert deployment_config_data to AgentDeployment instances
    deployment_config = []
    for deployment in deployment_config_data:
        try:
            deployment_instance = AgentDeployment(**deployment)
            deployment_config.append(deployment_instance)
        except Exception as e:
            logger.error(f"Failed to parse deployment: {str(e)}")

    if not deployment_config:
        raise ValueError("No valid deployments found in deployment.json.")

    # Parse command-line arguments
    args = parse_arguments()

    # Process options into a list
    options_list = [option.strip() for option in args.options.split(',') if option.strip()]
    if not options_list:
        raise ValueError("At least one option must be provided.")

    # Prepare input data
    input_params = InputSchema(
        func_name="func",
        func_input_data={
            args.question: options_list,
        },
        llm_config_name=args.llm_config_name,
        agent_count=args.agent_count,
    )

    module_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=deployment_config[0],  # Pass a single AgentDeployment instance
        consumer_id=naptha.user.id,
    )

    response = run(module_run)
    print("Response: ", response)
