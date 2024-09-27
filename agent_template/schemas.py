from pydantic import BaseModel, Field

class InputSchema(BaseModel):
    prompt: str = Field(..., title="Prompt to be passed as input.")