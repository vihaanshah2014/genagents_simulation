#!/usr/bin/env python
import os
import json
import subprocess
from dotenv import load_dotenv
from naptha_sdk.schemas import AgentRunInput, OrchestratorRunInput, EnvironmentRunInput
from naptha_sdk.utils import get_logger
from module_template.schemas import InputSchema
from typing import Union

load_dotenv()

logger = get_logger(__name__)

# Basic module definition
class BasicModule:
    def __init__(self, module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput]):
        self.module_run = module_run

    def func(self, input_data):
        logger.info("Running module function")

        # Get the agent configuration
        agent_config = self.module_run.agent_deployment.agent_config

        # Get the LLM config from agent_config
        llm_config = agent_config.llm_config

        # Extract necessary parameters
        model = getattr(llm_config, 'model', 'gpt-3.5-turbo')
        temperature = getattr(llm_config, 'temperature', 0.7)
        max_tokens = getattr(llm_config, 'max_tokens', 1000)
        api_base = getattr(llm_config, 'api_base', 'https://api.openai.com/v1')
        client = getattr(llm_config, 'client', 'openai')

        # Check if the client is 'openai'
        if client == 'openai':
            # Prepare the API key and endpoint
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return "OpenAI API key not found in environment variables."

            # Prepare the headers and data for the request
            headers = [
                "Content-Type: application/json",
                f"Authorization: Bearer {api_key}"
            ]

            # Prepare the data payload
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "If you were a human, what would your first words be?"
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Convert data to JSON string
            data_json = json.dumps(data)

            # Build the curl command
            curl_command = [
                "curl",
                "-X", "POST",
                f"{api_base}/chat/completions",
                "-H", headers[0],
                "-H", headers[1],
                "-d", data_json
            ]

            # Execute the curl command
            try:
                result = subprocess.run(
                    curl_command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Parse the response
                response = json.loads(result.stdout)
                content = response['choices'][0]['message']['content']
                return content.strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"Curl command failed: {e.stderr}")
                return "Failed to get response from OpenAI API."
            except Exception as e:
                logger.error(f"Error: {e}")
                return "An error occurred."
        else:
            # Handle other clients if needed
            return "Client not supported."

# Default entrypoint when the module is executed
def run(module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput]):
    basic_module = BasicModule(module_run)
    method = getattr(basic_module, module_run.inputs.func_name, None)
    return method(module_run.inputs.func_input_data)

if __name__ == "__main__":
    # For testing locally
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments

    naptha = Naptha()

    input_params = InputSchema(func_name="func", func_input_data="gm...")

    # Load Configs
    agent_deployments = load_agent_deployments(
        "module_template/configs/agent_deployments.json",
        load_persona_data=False,
        load_persona_schema=False
    )

    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0],
        consumer_id=naptha.user.id,
    )

    response = run(agent_run)

    print("Response:\n", response)
