from fastapi import APIRouter,status,HTTPException,Request,BackgroundTasks
from fastapi.responses import JSONResponse
from src.schemas.classes import PromptInput
from policy.module import policy
from src.db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.db.modules import log_prompt
from src.db.redis import add_prompt_memory
import asyncio
from ml_model.function import ml_scan
router = APIRouter()
#changed to taskgroup
@router.post('', status_code=status.HTTP_200_OK)
async def prompt_input(prompt: PromptInput, request: Request,background_tasks: BackgroundTasks):
    client = request.app.state.http_client
    sanitize_policy = request.app.state.sanitize_policy
    bloom_filter = request.app.state.bloom_filter
    model = request.app.state.model
    vectorizer = request.app.state.vectorizer
    raw_prompt = policy(prompt.prompt)
    raw_prompt.normalize_prompt
    async with asyncio.TaskGroup() as tg:
        ml_score = tg.create_task(asyncio.to_thread(ml_scan,prompt.prompt,model=model,vectorizer=vectorizer))
        sanitize_task = tg.create_task(asyncio.to_thread(raw_prompt.sanitize_prompt, sanitize_policy=sanitize_policy, bloom_filter=bloom_filter))
        scan_task = tg.create_task(raw_prompt.scan_prompt(client=client))
    regex_sanitize,regex_decision,sanitized_prompt,sanitized_words  = sanitize_task.result()
    scan = scan_task.result()
    ml_score = ml_score.result() * 100
    # print(entropy)
    if scan['block'] == True:

        decision = "BLOCK"
        background_tasks.add_task(log_prompt,prompt,decision,scan["violations"],ml_score)
        print(ml_score)
        return JSONResponse(
            status_code= status.HTTP_406_NOT_ACCEPTABLE,
            content = {"detail": f"prompt injection detected violating rule {scan["violations"]}"},
            background=background_tasks
        )
    if ml_score > 90:
        decision = "BLOCK"
        background_tasks.add_task(log_prompt,prompt,["FLAGGED"],decision,ml_score)
        return JSONResponse(
            status_code= status.HTTP_406_NOT_ACCEPTABLE,
            content = {"detail": f"prompt injection {ml_score}% injection score"},
            background=background_tasks
        )
    if len(sanitized_words) > 0 or regex_decision == "SANITIZE":
        decision = "SANITIZE"
    else:
        decision = "ALLOW"
    prompt.prompt = sanitized_prompt
    background_tasks.add_task(log_prompt,prompt,decision,sanitized_words,ml_score)
    #serves as memory write tool example
    redis_write =await add_prompt_memory(prompt.user_id,prompt.role,sanitized_prompt)
    return sanitized_prompt