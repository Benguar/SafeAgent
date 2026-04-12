from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.routes import prompt,output,tool_output
import httpx
import re
import yaml
import traceback
from src.db.models import create_table
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yaml_path = "policy/policy.yaml"
        sanitize_policy = []
        with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        for rule in config.get('sanitize', []):
            try:
                pattern = re.compile(rule['pattern'], re.IGNORECASE)
                sanitize_policy.append({
                    'pattern': pattern,
                    'action': rule['action'],
                    'name': rule['name']
                })
            except re.error as e:
                print(e)
        app.state.sanitize_policy = sanitize_policy
        app.state.http_client = httpx.AsyncClient()
        await create_table()
        yield
        await app.state.http_client.aclose()
    except Exception as e:
         print("lifespan broken")
         traceback.print_exc()

version = 'v1'
app = FastAPI(
    version= version,
    lifespan=lifespan
)

app.include_router(prompt.router,prefix=f'/{version}/safeagent/prompt')