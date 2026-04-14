from sqlalchemy.orm import DeclarativeBase,mapped_column,Mapped
from sqlalchemy import func,DateTime
from sqlalchemy.dialects.postgresql import JSONB
from uuid6 import uuid7
import uuid
from datetime import datetime,timedelta
from src.db.connection import engine
class Base(DeclarativeBase):
    pass

class Logs(Base):
    __tablename__ = "sdk_logging"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,nullable=False,default=uuid7)
    user_id: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)
    decision: Mapped[str] = mapped_column(nullable=False)
    violations: Mapped[list] = mapped_column(type_=JSONB,nullable=False,default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)