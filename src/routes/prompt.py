from fastapi import APIRouter,status,HTTPException, Request
from src.schemas.classes import PromptInput
from src.db.models import Logs
from policy.module import policy
import asyncio
router = APIRouter(
    tags=["prompt_input"]
)

@router.post('', status_code=status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput, request: Request):
    client = request.app.state.http_client
    sanitize_policy = request.app.state.sanitize_policy
    raw_prompt = policy(prompt.prompt)
    raw_prompt.normalize_prompt()
    check_entropy = asyncio.to_thread(raw_prompt.check_secrets)
    scan,entropy = await asyncio.gather(raw_prompt.scan_prompt(client=client), check_entropy)
    print(entropy)
    if scan['block'] == True:
        #background task for logging  postgres comes here 
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f'prompt injection detected violating rule {scan["violations"]}')
    raw_prompt = policy(entropy)
    sanitized_prompt = raw_prompt.sanitize_prompt(sanitize_policy=sanitize_policy)
    return sanitized_prompt