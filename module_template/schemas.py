from pydantic import BaseModel, Field
from typing import Union, Dict, Any

class InputSchema(BaseModel):
    func_name: str
    func_input_data: Union[list, str, Dict[str, Any]]
    context: str = Field(default="")
