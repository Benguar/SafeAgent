from src.config.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import sessionmaker

try:
    url = settings.DATABASE_URL
    engine = create_async_engine(url)
    asyncsession = async_sessionmaker(bind=engine,autoflush=False,autocommit=False)

    async def get_db():
        async with asyncsession() as session:
            yield session
    print("success")
except Exception as e:
    print(f'error is {e}')



