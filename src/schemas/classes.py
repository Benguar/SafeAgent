from pydantic import BaseModel,Field

class PromptInput(BaseModel):
    user_id: int|None = None #optional for now for testing purposes 
    role: str|None = None #optional for now for testing purposes
    prompt: str = Field(min_length=1,max_length=2000)