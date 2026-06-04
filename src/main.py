from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.routes import final_output, prompt,tool_output
import httpx
import re
import yaml
import traceback
from src.db.models import create_table
from rbloom import Bloom
from words.bloom_filter import bloom_hash
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
        app.state.bloom_filter = Bloom.load("words/words.bloom", hash_func= bloom_hash)
        app.state.sanitize_policy = sanitize_policy
        limits = httpx.Limits(keepalive_expiry=120.0)
        app.state.http_client = httpx.AsyncClient(limits=limits)
        await create_table()
        yield
        await app.state.http_client.aclose()
    except Exception as e:
         print("lifespan broken")
         traceback.print_exc()
         raise e 

version = 'v1'
app = FastAPI(
    version= version,
    lifespan=lifespan
)

app.include_router(prompt.router,prefix=f'/{version}/safeagent/prompt',tags=["prompt_input"])
app.include_router(tool_output.router,prefix=f'/{version}/safeagent/tool_output',tags=["tool_output"])
app.include_router(final_output.router,prefix=f'/{version}/safeagent/final_output',tags=["final_output"])