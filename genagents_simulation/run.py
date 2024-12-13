#!/usr/bin/env python
import os
import json
import subprocess
import random
from dotenv import load_dotenv
from typing import Union, Dict, Any, List
from naptha_sdk.schemas import AgentRunInput, OrchestratorRunInput, EnvironmentRunInput
from naptha_sdk.utils import get_logger
from genagents_simulation.schemas import InputSchema
from genagents_simulation.simulation_engine.global_methods import *
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
    import argparse
    import json
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments

    TOTAL_AGENTS = 3505  # Total number of available agents

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run agent simulations')
    parser.add_argument('command', choices=['simulate'], help='Command to execute')
    parser.add_argument('-p', '--params', nargs='+', help='Parameters in format key=value', required=True)
    parser.add_argument('--llm', default='model_2', help='LLM config to use')
    parser.add_argument('--show-explanations', action='store_true', help='Show individual agent explanations')
    parser.add_argument('--raw-output', action='store_true', help='Show raw response object without formatting')

    args = parser.parse_args()

    # Parse parameters
    params = {}
    for param in args.params:
        key, value = param.split('=', 1)
        # Remove any surrounding quotes
        value = value.strip('\'"')
        params[key] = value

    # Required parameters
    required_params = ['prompt', 'question', 'type', 'agents']
    for param in required_params:
        if param not in params:
            parser.error(f"Missing required parameter: {param}")

    # Handle categorical type
    if params['type'] == 'categorical' and 'options' not in params:
        parser.error("Categorical type requires 'options' parameter (comma-separated list)")

    # Process options if provided
    if 'options' in params:
        params['options'] = [opt.strip() for opt in params['options'].split(',')]

    # Convert agents parameter to int
    if params['agents'].endswith('%'):
        percentage = float(params['agents'].rstrip('%'))
        agent_count = int((percentage / 100) * TOTAL_AGENTS)
        # Ensure at least 1 agent
        agent_count = max(1, agent_count)
    else:
        agent_count = int(params['agents'])
        # Cap at maximum available agents
        agent_count = min(agent_count, TOTAL_AGENTS)

    # Set up naptha client
    naptha = Naptha()
    agent_deployments = load_agent_deployments(
        "genagents_simulation/configs/agent_deployments.json",
        load_persona_data=False,
        load_persona_schema=False,
    )

    # Prepare input based on type
    if params['type'] == 'categorical':
        test_questions = {f"{params['prompt']}\n{params['question']}": params['options']}
    else:
        # Handle open-ended questions when implemented
        raise NotImplementedError("Open-ended questions not yet implemented")

    # Prepare and run simulation
    input_params = InputSchema(func_name="func", func_input_data=test_questions)
    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0] if agent_deployments else None,
        consumer_id=naptha.user.id,
    )

    print(f"\nRunning simulation with {agent_count} agents...")
    response = run(agent_run, args.llm, agent_count=agent_count)

    # Print results
    for question, data in response['summary'].items():
        print(f"\nResults for: {question}")
        print("\nResponses:")
        for option, visual in data['visual'].items():
            print(f"{option}: {visual}")
        print("\nPercentages:")
        for option, percentage in data['percentages'].items():
            print(f"{option}: {percentage}")
        
        # Show explanations if requested
        if args.show_explanations:
            print("\nExplanations:")
            for i, explanation in enumerate(data['explanations'], 1):
                print(f"\nAgent {i}:")
                print(explanation)