from fastapi import APIRouter,status,HTTPException
from src.schemas.classes import PromptInput
from policy.module import scan_prompt,sanitize_prompt
router = APIRouter(
    tags=["prompt_input"]
)

@router.post('', status_code=status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput):
    scan = await scan_prompt(prompt.prompt)
    if scan['block'] == True:
        #background task for logging  postgres comes here 
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f'prompt injection detected violating rule {id}')
    sanitized_prompt = sanitize_prompt(prompt.prompt)
    print(sanitized_prompt)
    return sanitized_prompt