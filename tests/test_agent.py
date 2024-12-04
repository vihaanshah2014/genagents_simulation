from naptha_sdk.client.naptha import Naptha
from naptha_sdk.schemas import AgentRunInput
from naptha_sdk.configs import load_agent_deployments
from module_template.schemas import InputSchema

def test_agent_memory():
    naptha = Naptha()

    # Load agent deployment config
    agent_deployments = load_agent_deployments(
        "module_template/configs/agent_deployments.json", 
        load_persona_data=False, 
        load_persona_schema=False
    )

    # Test sequence of interactions
    test_inputs = [
        "Hello, I'm a user talking to you.",
        "What's the weather like today?",
        "Let's have a conversation about AI."
    ]

    # Store agent's state between interactions
    agent_state = None

    for input_text in test_inputs:
        # Create input parameters
        input_params = InputSchema(
            func_name="func",
            func_input_data=input_text,
            context=str(agent_state) if agent_state else ""
        )

        # Create agent run input
        agent_run = AgentRunInput(
            inputs=input_params,
            agent_deployment=agent_deployments[0],
            consumer_id=naptha.user.id,
        )

        # Run the agent
        from module_template.run import run
        response = run(agent_run)

        # Print the interaction
        print("\n=== New Interaction ===")
        print(f"User: {input_text}")
        print(f"Response: {response['response']}")
        print("\nAgent State:")
        print(f"- ID: {response['agent_state']['id']}")
        print(f"- Scratch Memory: {response['agent_state']['scratch']}")
        print("\nMemories:")
        for memory in response['agent_state']['memories']:
            print(f"- {memory}")

        # Update agent state for next interaction
        agent_state = response['agent_state']

if __name__ == "__main__":
    test_agent_memory() 