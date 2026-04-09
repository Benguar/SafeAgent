from fastapi import APIRouter,status,HTTPException
from src.schemas.classes import PromptInput
from policy.module import policy
import asyncio
router = APIRouter(
    tags=["prompt_input"]
)

@router.post('', status_code=status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput):
    raw_prompt = policy(prompt.prompt)
    raw_prompt.normalize_prompt()
    check_entropy = asyncio.to_thread(raw_prompt.check_secrets)
    scan,entropy = await asyncio.gather(raw_prompt.scan_prompt(), check_entropy)
    print(entropy)
    if scan['block'] == True:
        #background task for logging  postgres comes here 
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f'prompt injection detected violating rule {scan["violations"]}')
    raw_prompt = policy(entropy)
    sanitized_prompt = raw_prompt.sanitize_prompt()
    return sanitized_prompt