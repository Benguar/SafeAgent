from fastapi import FastAPI
from src.routes import prompt,output,tool_output

version = 'v1'

app = FastAPI(
    version= version
)

app.include_router(prompt.router,prefix=f'/{version}/safeagent/prompt')