import redis.asyncio as aioredis
from src.config.settings import settings
from datetime import datetime,timezone
import json
prompt_telemetry = aioredis.StrictRedis(
    host= settings.REDIS_HOST,
    port= settings.REDIS_PORT,
    db=0,
    decode_responses= True
)

async def add_prompt_memory(id,role,prompt):
    data = {"role": role,'system_prompt': settings.SYSTEM_PROMPT,'prompt': prompt,'added_at': datetime.now(timezone.utc).isoformat()}
    json_data = json.dumps(data)
    await prompt_telemetry.rpush(
    id,json_data
    )