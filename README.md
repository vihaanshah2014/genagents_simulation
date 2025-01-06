# GenAgents Simulation Module

GenAgents Simulation is a powerful Naptha Module designed to simulate interactions and responses from a vast population of generative agents. With **3,505 total agents**, this module enables the creation of complex multi-agent environments, social simulations, and large-scale testing scenarios. Whether you're building social simulations, testing AI behaviors, or creating dynamic environments, GenAgents Simulation provides the flexibility and scalability you need.

## Table of Contents

- [🔍 Overview](#-overview)
- [🚀 Features](#-features)
- [🛠 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [💻 Usage](#-usage)
  - [Command Syntax](#command-syntax)
  - [Example Commands](#example-commands)
- [🌐 Deployment](#-deployment)
- [📊 Understanding the Output](#-understanding-the-output)
- [📜 License](#-license)

## 🔍 Overview

GenAgents Simulation leverages large language models (LLMs) to generate realistic and diverse agent behaviors. Each agent can simulate responses based on predefined personas, configurations, and prompts, allowing for intricate simulations of social dynamics, decision-making processes, and more.

### Key Highlights

- **Massive Agent Pool:** Simulate interactions with up to **3,505 agents**, enabling large-scale simulations.
- **Customizable Configurations:** Tailor agent behaviors using detailed configurations in `deployment.json`.
- **Dynamic Responses:** Agents generate responses based on the latest LLM configurations, ensuring up-to-date and relevant interactions.
- **Scalable Architecture:** Designed to run efficiently on local machines or distributed Naptha Nodes.

## 🚀 Features

- **Flexible Input Parameters:** Customize questions, options, LLM configurations, and agent counts via command-line arguments.
- **Detailed Summaries:** Receive comprehensive summaries of agent responses, including counts, percentages, visual representations, and explanations.
- **Extensible Design:** Easily extendable to accommodate new agent behaviors, personas, and configurations.

## 🛠 Installation

### Prerequisites

- **Python 3.12** or higher
- **Poetry** for dependency management
- **Naptha SDK** installed and configured

### Install Poetry

If you haven't installed Poetry yet, follow these steps:

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Clone the Repository

```bash
git clone https://github.com/vihaan.shah2014/genagents_simulation
cd genagents_simulation
```

### Install Dependencies

```bash
poetry install
```

### Setup Environment Variables

Create a copy of the `.env.example` file:

```bash
cp .env.example .env
```

Edit the `.env` file to include necessary environment variables, such as `PRIVATE_KEY` and `OPENAI_API_KEY` if using OpenAI.

## ⚙️ Configuration

### Deployment Configuration

The `deployment.json` file located in `genagents_simulation/configs/` defines how agents are deployed and configured. Here's a sample structure:

```json
[
    {
        "name": "deployment_1",
        "module": {"name": "genagents_simulation"},
        "node": {"ip": "localhost", "port": 7001},
        "config": {
            "config_name": "agent_config_1",
            "llm_config": {"config_name": "model_2"},
            "persona_module": {
                "url": "https://huggingface.co/datasets/richardblythman/characterfile_richardblythman"
            },
            "system_prompt": {
                "role": "You are a helpful AI assistant.",
                "persona": ""
            }
        }
    }
]
```

Ensure that each deployment entry includes all required fields as per the `AgentDeployment` schema.

### LLM Configurations

LLM configurations are defined in `llm_configs.json`. Customize these to change the underlying language models used by the agents.

## 💻 Usage

GenAgents Simulation can be executed directly via the command line, allowing you to specify custom questions, options, LLM configurations, and the number of agents.

### Command Syntax

```bash
python genagents_simulation/run.py --question "<YOUR_QUESTION>" --options "<OPTION1,OPTION2,...>" [--llm_config_name "<LLM_CONFIG>"] [--agent_count <NUMBER>]
```

### Example Commands

1. **Basic Usage**

    Simulate a single agent answering a simple question:

    ```bash
    python genagents_simulation/run.py --question "Do you support increasing the minimum wage?" --options "Yes,No,Undecided"
    ```

2. **Specify LLM Configuration and Multiple Agents**

    Run the simulation with a specific LLM configuration and multiple agents:

    ```bash
    python genagents_simulation/run.py --question "Should public transportation be free?" --options "Yes,No,Depends" --llm_config_name "model_3" --agent_count 5
    ```

3. **Custom LLM Configuration**

    Use a different LLM configuration for varied responses:

    ```bash
    python genagents_simulation/run.py --question "Is climate change a significant threat?" --options "Yes,No" --llm_config_name "model_4" --agent_count 10
    ```

## 🌐 Deployment

### Running Locally

Ensure that your Naptha Node and Hub are running locally. Then execute the module using the command syntax provided above.

### Deploying to a Naptha Node

1. **Register the Module**

    Register your module on the Naptha Hub:

    ```bash
    naptha agents genagents_simulation -p "description='GenAgents Simulation Module' url='ipfs://<YOUR_IPFS_HASH>' type='package' version='1.0'"
    ```

2. **Run the Module on the Node**

    Execute the module on your Naptha Node:

    ```bash
    naptha run agent:genagents_simulation --question "Do you support increasing the minimum wage?" --options "Yes,No,Undecided" --llm_config_name "model_2" --agent_count 1
    ```

## 📊 Understanding the Output

When you run the simulation, the output will be a JSON object containing:

- **individual_responses**: Each agent's response and reasoning.
- **summary**: Aggregated data including counts, percentages, visual representations, and explanations for each option.
- **num_agents**: The total number of agents that participated in the simulation.

### Sample Output

```json
{
    "individual_responses": [
        {
            "responses": ["Yes"],
            "reasonings": ["Given the participant's slightly liberal political views and their emphasis on the importance of community and social impact in their work, it is reasonable to predict that they would support increasing the minimum wage. They have not indicated any strong opposition to social welfare policies."]
        }
    ],
    "summary": {
        "Do you support increasing the minimum wage?": {
            "counts": {"Yes": 1, "No": 0, "Undecided": 0},
            "percentages": {"Yes": "100.0%", "No": "0.0%", "Undecided": "0.0%"},
            "visual": {"Yes": "████████████████████ 1/1", "No": " 0/1", "Undecided": " 0/1"},
            "explanations": [
                "Given the participant's slightly liberal political views and their emphasis on the importance of community and social impact in their work, it is reasonable to predict that they would support increasing the minimum wage. They have not indicated any strong opposition to social welfare policies."
            ]
        }
    },
    "num_agents": 1
}
```

### Breakdown

- **individual_responses**: Detailed responses from each agent, including their reasoning.
- **summary**: Aggregated results showing how many agents chose each option, the percentage breakdown, visual bars representing the distribution, and aggregated explanations.
- **num_agents**: Indicates the number of agents that participated.
---

For further assistance or to contribute, please contact me at [vihaan.shah2014@gmail.com](mailto:vihaan.shah2014@gmail.com).
