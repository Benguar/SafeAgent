from fastapi import APIRouter,status,HTTPException
from src.schemas.classes import PromptInput

router = APIRouter(
    tags=["prompt_input"]
)

@router.post('', status_code= status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput):
    return 'success'