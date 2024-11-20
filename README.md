# Module Template

This is a base template for creating agent, agent orchestrator, and environment modules. You can check out other examples of agent, orchestrator and environment modules using the CLI commands with the [Naptha SDK](https://github.com/NapthaAI/naptha-sdk). 

## Pre-Requisites 

### Install Poetry 

From the official poetry [docs](https://python-poetry.org/docs/#installing-with-the-official-installer):

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/home/$(whoami)/.local/bin:$PATH"
```

### Install the Naptha SDK

Install the Naptha SDK using the [instructions here](https://github.com/NapthaAI/naptha-sdk).

### (Optional) Run your own Naptha Node

You can run your own Naptha node using the [instructions here](https://github.com/NapthaAI/node) (still private, please reach out if you'd like access).

## Clone and Install the Module

Clone the repo using:

```bash
git clone https://github.com/NapthaAI/module_template
cd module_template
```

You can install the module using:

```bash
poetry install
```

Don't forget to change the name of the agent.

## Prototyping the Module

Before deploying to a Naptha node, you should iterate on improvements with the module locally. You can run the module using:

```bash
poetry run python <module_name>/run.py
```

When ready, you can push to your GitHub account or IPFS (or both). Make sure to add a version number using:

```bash
git tag v0.1
```

```bash
git push --tags
```

## Register the Module on the Naptha Hub

If creating an agent module, you can register it on the Naptha Hub using:

```bash
naptha agents agent_name -p "description='Agent description' url='ipfs://QmNer9SRKmJPv4Ae3vdVYo6eFjPcyJ8uZ2rRSYd3koT6jg' type='package' version='0.1'" 
```

If creating an orchestrator module, you can register it on the Naptha Hub using:

```bash
naptha orchestrators orchestrator_name -p "description='Orchestrator description' url='ipfs://QmNer9SRKmJPv4Ae3vdVYo6eFjPcyJ8uZ2rRSYd3koT6jg' type='package' version='0.1'" 
```

If creating an environment module, you can register it on the Naptha Hub using:

```bash
naptha environments environment_name -p "description='Environment description' url='ipfs://QmNer9SRKmJPv4Ae3vdVYo6eFjPcyJ8uZ2rRSYd3koT6jg' type='package' version='0.1'" 
```

Make sure to replace the placeholder descriptions and URLs with your own.
