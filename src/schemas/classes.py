from pydantic import BaseModel,Field

class PromptInput(BaseModel):
    user_id: str = '019d8917-5376-78f6-8cb4-ae7f3b584727' #optional for now for testing purposes 
    role: str = "user" #optional for now for testing purposes
    prompt: str = Field(min_length=1,max_length=2000)