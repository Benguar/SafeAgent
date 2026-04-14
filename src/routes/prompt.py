from fastapi import APIRouter,status,HTTPException, Request,Depends,BackgroundTasks
from fastapi.responses import JSONResponse
from src.schemas.classes import PromptInput
from src.db.models import Logs
from policy.module import policy
from src.db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.db.modules import log_postgres
import asyncio

router = APIRouter()

@router.post('', status_code=status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput, request: Request,background_tasks: BackgroundTasks,db: AsyncSession = Depends(get_db)):
    client = request.app.state.http_client
    sanitize_policy = request.app.state.sanitize_policy
    raw_prompt = policy(prompt.prompt)
    raw_prompt.normalize_prompt()
    check_entropy = asyncio.to_thread(raw_prompt.check_secrets)
    scan,(entropy,sanitized_words) = await asyncio.gather(raw_prompt.scan_prompt(client=client), check_entropy)
    print(entropy)
    if scan['block'] == True:
        # query = await db.execute(insert(Logs).values(**prompt.model_dump(),decision = "BLOCK",violations = scan["violations"]))
        # await db.commit()
        background_tasks.add_task(log_postgres,prompt,"BLOCK",scan["violations"])
        return JSONResponse(
            status_code= status.HTTP_406_NOT_ACCEPTABLE,
            content = {"detail": f"prompt injection detected violating rule {scan["violations"]}"},
            background=background_tasks
        )
        # raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f'prompt injection detected violating rule {scan["violations"]}')
    raw_prompt = policy(entropy)
    sanitized_prompt,decision = raw_prompt.sanitize_prompt(sanitize_policy=sanitize_policy)
    if len(sanitized_words) > 0 or decision == "SANITIZE":
        prompt.prompt = sanitized_prompt
        background_tasks.add_task(log_postgres,prompt,"SANITIZE",sanitized_words)
    else:
        prompt.prompt = sanitized_prompt
        background_tasks.add_task(log_postgres,prompt,"ALLOW",sanitized_words)
    print(sanitized_words)
    return sanitized_prompt

