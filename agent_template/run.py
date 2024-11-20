#!/usr/bin/env python
from naptha_sdk.schemas import AgentRunInput, OrchestratorRunInput, EnvironmentRunInput
from naptha_sdk.utils import get_logger
from module_template.schemas import InputSchema
from typing import Union

logger = get_logger(__name__)

# You can create your module as a class or function
class BasicModule:
    def __init__(self, module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput]):
        self.module_run = module_run

    def func(self, inputs: InputSchema):
        logger.info(f"Running module function: {inputs.func_name}")
        return "Module function executed successfully"

# Default entrypoint when the module is executed
def run(module_run: Union[AgentRunInput, OrchestratorRunInput, EnvironmentRunInput]):
    basic_module = BasicModule(module_run)
    method = getattr(basic_module, module_run.inputs.func_name, None)
    return method(module_run.inputs)

if __name__ == "__main__":
    # For testing locally
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import load_agent_deployments, load_environment_deployments, load_orchestrator_deployments

    naptha = Naptha()

    input_params = InputSchema(prompt="gm...")
        
    # Load Configs
    agent_deployments = load_agent_deployments("module_template/configs/agent_deployments.json")
    # orchestrator_deployments = load_orchestrator_deployments("module_template/configs/orchestrator_deployments.json")
    # environment_deployments = load_environment_deployments("module_template/configs/environment_deployments.json")

    agent_run = AgentRunInput(
        inputs=input_params,
        agent_deployment=agent_deployments[0],
        consumer_id=naptha.user.id,
    )

    # orchestrator_run = OrchestratorRunInput(
    #     inputs=input_params,
    #     agent_deployments=agent_deployments,
    #     orchestrator_deployment=orchestrator_deployments[0],
    #     environment_deployments=environment_deployments,
    #     consumer_id=naptha.user.id,
    # )

    # environment_run = EnvironmentRunInput(
    #     inputs=input_params,
    #     environment_deployment=environment_deployments[0],
    #     consumer_id=naptha.user.id,
    # )

    run(agent_run)
