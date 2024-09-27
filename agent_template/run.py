#!/usr/bin/env python
from agent_template.schemas import InputSchema
from naptha_sdk.utils import get_logger, load_yaml

logger = get_logger(__name__)

def run(inputs, worker_nodes=None, orchestrator_node=None, flow_run=None, cfg=None):
    logger.info(f"Inputs: {inputs}")
    return None

if __name__ == "__main__":
    cfg_path = "agent_template/component.yaml"
    cfg = load_yaml(cfg_path)
    inputs = InputSchema(prompt="hi")
    run(inputs, cfg=cfg)