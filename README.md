# Template

This is a base template for creating agents and multi-agent networks. You can check out other examples of agents and multi-agent networks at https://github.com/NapthaAI. 

## Pre-Requisites 

### Install Poetry 

From the official poetry [docs](https://python-poetry.org/docs/#installing-with-the-official-installer):

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/home/$(whoami)/.local/bin:$PATH"
```

### Clone and Install the Agent

Clone the repo using:

```bash
git clone https://github.com/NapthaAI/agent_template
cd agent_template
```

You can install the module using:

```bash
poetry install
```

Don't forget to change the name of the agent.

## Prototyping the Agent

Before deploying to a Naptha node, you should iterate on improvements with the agent locally. You can run the agent using:

```bash
poetry run python <agent_name>/run.py
```

When ready, let's push to your own GitHub or HuggingFace account. Add a version number using:

```bash
git tag v0.1
```

Then push using:

```bash
git push --tags
```
