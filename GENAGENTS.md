# Running GenAgents on Naptha Node

This guide explains how to run generative agent simulations using the Naptha node.

## Quick Start

You can run simulations using the following command structure:
```bash
poetry run python -m module_template.run simulate -p <parameters>
```

### Required Parameters

- `prompt`: Context or setup for the question
- `question`: The actual question to ask
- `type`: Type of response (`categorical` only for now)
- `agents`: Number of agents (integer) or percentage (e.g., "10%")
- `options`: Comma-separated list of possible answers (required for categorical questions)

### Optional Flags

- `--llm`: Specify LLM config to use (default: 'model_2')
- `--show-explanations`: Show individual agent explanations
- `--raw-output`: Show raw JSON response without formatting

## Examples

### Basic Categorical Question
```bash
poetry run python -m module_template.run simulate -p \
    prompt="You are a resident of New York" \
    question="What's your preferred method of transportation?" \
    type=categorical \
    options="Subway,Bus,Walking,Taxi" \
    agents=50
```

### Using Percentage of Available Agents
```bash
poetry run python -m module_template.run simulate -p \
    prompt="You are a tech professional" \
    question="What programming language do you prefer?" \
    type=categorical \
    options="Python,JavaScript,Java,C++" \
    agents=10%
```

### With Explanations
```bash
poetry run python -m module_template.run simulate -p \
    prompt="You are a movie enthusiast" \
    question="What's your favorite movie genre?" \
    type=categorical \
    options="Action,Comedy,Drama,Horror,Sci-Fi" \
    agents=25 \
    --show-explanations
```

### Raw Output
```bash
poetry run python -m module_template.run simulate -p \
    prompt="You are a food critic" \
    question="What's your favorite cuisine?" \
    type=categorical \
    options="Italian,Chinese,Mexican,Indian" \
    agents=5 \
    --raw-output
```

## Notes

- Total available agents: 3505
- When using percentage (e.g., "10%"), the number of agents will be calculated based on the total available agents
- Maximum agents is capped at 3505
- Minimum agents is 1, even when using small percentages
- The `--show-explanations` flag will show each agent's reasoning for their choice
- The `--raw-output` flag returns the complete response object in JSON format

## Troubleshooting

1. If you get "Module not found" errors:
   ```bash
   poetry install
   ```

2. If you need to update environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. If you need to use a different LLM:
   - Check available configs in `module_template/configs/llm_configs.json`
   - Use the `--llm` flag with the desired config name