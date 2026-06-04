from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.connection import get_db,asyncsession
from sqlalchemy import insert
from src.db.models  import Prompt_logs,Tool_logs,Final_output_logs
from src.schemas.classes import PromptInput,ToolInput,FinalOutput
import asyncio



async def log_prompt(value: PromptInput,decision: str,violations: list):
    async with asyncsession() as db:
        query = await db.execute(insert(Prompt_logs).values(**value.model_dump(),decision = decision,violations = violations))
        await db.commit()
async def log_tool_output(value: ToolInput,decision:str,violations: list):
    async with asyncsession() as db:
        query = await db.execute(insert(Tool_logs).values(**value.model_dump(),decision=decision,violations=violations))
        await db.commit()
async def log_final_output(value: FinalOutput,decision:str,violations: list):
    async with asyncsession() as db:
        query = await db.execute(insert(Final_output_logs).values(**value.model_dump(),decision=decision,violations=violations))
        await db.commit()