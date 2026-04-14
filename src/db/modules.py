from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.connection import get_db,asyncsession
from sqlalchemy import insert
from src.db.models  import Logs
from src.schemas.classes import PromptInput
import asyncio



async def log_postgres(values: PromptInput,decision: str,violations: list):
    async with asyncsession() as db:
        query = await db.execute(insert(Logs).values(**values.model_dump(),decision = decision,violations = violations))
        await db.commit()


