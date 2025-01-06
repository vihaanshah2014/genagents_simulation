from pydantic import BaseModel
from typing import Dict, List

class InputSchema(BaseModel):
    func_name: str
    func_input_data: Dict[str, List[str]]
    llm_config_name: str
    agent_count: int
