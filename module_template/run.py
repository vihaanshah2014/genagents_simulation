#!/usr/bin/env python
import os
import json
import subprocess
import random
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
    def __init__(self, module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput], llm_config_name: str, agent_count: Union[int, str] = 1):
        self.module_run = module_run
        self.llm_configs = load_llm_configs()
        if llm_config_name not in self.llm_configs:
            raise ValueError(f"LLM config '{llm_config_name}' not found in {LLM_CONFIG_PATH}")
        self.llm_config = self.llm_configs[llm_config_name]

        # Base paths for agents
        gss_base_path = os.path.join(os.path.dirname(__file__), "agent_bank/populations/gss_agents")
        single_agent_path = os.path.join(os.path.dirname(__file__), "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae")

        # Initialize agents based on count or percentage
        self.agents = []
        
        # Get all available GSS agents
        all_gss_agents = self._get_agent_folders(gss_base_path)
        
        if isinstance(agent_count, int):
            if agent_count == 1:
                selected_agents = [single_agent_path]
            else:
                # Randomly select the specified number of agents
                selected_agents = random.sample(all_gss_agents, min(agent_count, len(all_gss_agents)))
        else:
            # Handle percentage-based selection (e.g., "50%", "100%")
            percentage = int(agent_count.rstrip('%'))
            num_agents = max(1, int(len(all_gss_agents) * percentage / 100))
            # For percentages, take a continuous slice after a random start point
            start_idx = random.randint(0, len(all_gss_agents) - num_agents)
            selected_agents = all_gss_agents[start_idx:start_idx + num_agents]

        # Create agent instances
        for agent_path in selected_agents:
            try:
                agent = GenerativeAgent(agent_path)
                self.agents.append(agent)
            except Exception as e:
                logger.error(f"Failed to load agent: {str(e)}")

    def _get_agent_folders(self, base_path: str) -> List[str]:
        """Get list of agent folders from the GSS agents directory."""
        try:
            agent_folders = []
            for root, dirs, files in os.walk(base_path):
                if 'scratch.json' in files and 'meta.json' in files:
                    agent_folders.append(root)
            return sorted(agent_folders)  # Sort for consistent ordering
        except Exception as e:
            logger.error(f"Error accessing agent folders: {str(e)}")
            return []

    def func(self, questions: Dict[str, List[str]]):
        """
        Generate categorical responses to questions using all initialized agents.
        questions: Dictionary of questions and their possible answers
        """
        logger.info(f"Running func method in BasicModule with {len(self.agents)} agents")

        all_responses = []
        response_counts = {}
        explanations = {}

        # Initialize response counts for each question
        for question in questions:
            response_counts[question] = {}
            explanations[question] = []
            for option in questions[question]:
                response_counts[question][option] = 0

        # Collect responses and count them
        for agent in self.agents:
            agent_response = agent.categorical_resp(questions)
            all_responses.append(agent_response)
            
            # Count responses and store explanations
            for q_idx, question in enumerate(questions):
                response = agent_response['responses'][q_idx]
                reasoning = agent_response['reasonings'][q_idx]
                response_counts[question][response] += 1
                explanations[question].append(reasoning)

        # Create visual representation
        visual_summary = {}
        for question in questions:
            total = sum(response_counts[question].values())
            visual_summary[question] = {
                'counts': response_counts[question],
                'percentages': {
                    option: f"{(count/total*100):.1f}%" 
                    for option, count in response_counts[question].items()
                },
                'visual': {
                    option: f"{'█' * int(count/total*20)}{count}/{total}" 
                    for option, count in response_counts[question].items()
                },
                'explanations': explanations[question]
            }

        return {
            "individual_responses": all_responses,
            "summary": visual_summary,
            "num_agents": len(self.agents)
        }

# Default entrypoint when the module is executed
def run(module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput], 
        llm_config_name: str,
        agent_count: Union[int, str] = 1):
    basic_module = BasicModule(module_run, llm_config_name, agent_count)
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

    # Test questions for categorical responses
    test_questions = {
        "If you were a superhero, what would be your primary power?": ["Mind Reading", "Time Travel", "Shapeshifting", "Invisibility", "Super Strength", "Super Speed"]
    }

    input_params = InputSchema(func_name="func", func_input_data=test_questions)
    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0] if agent_deployments else None,
        consumer_id=naptha.user.id,
    )

    # Example usage with different agent counts:
    # Single agent (default)
    # response = run(agent_run, "model_2")
    # print("\nSingle agent response:")
    # for question, data in response['summary'].items():
    #     print(f"\nQuestion: {question}")
    #     for option, visual in data['visual'].items():
    #         print(f"{option}: {visual}")
    #     print("\nExplanations:")
    #     for exp in data['explanations']:
    #         print(f"- {exp}")

    # 5 GSS agents
    response = run(agent_run, "model_2", agent_count=20)
    print("\n5 agents response:")
    for question, data in response['summary'].items():
        print(f"\nQuestion: {question}")
        for option, visual in data['visual'].items():
            print(f"{option}: {visual}")
        # Uncomment to see explanations
        # print("\nExplanations:")
        # for exp in data['explanations']:
        #     print(f"- {exp}")

    # # Test with 25% of available agents
    # response = run(agent_run, "model_2", agent_count="25%")
    # print("\n25% of agents response:")
    # for question, data in response['summary'].items():
    #     print(f"\nQuestion: {question}")
    #     for option, visual in data['visual'].items():
    #         print(f"{option}: {visual}")
    #     print("\nPercentages:")
    #     for option, percentage in data['percentages'].items():
    #         print(f"{option}: {percentage}")
        # Uncomment to see explanations
        # print("\nExplanations:")
        # for exp in data['explanations']:
        #     print(f"- {exp}")