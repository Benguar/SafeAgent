import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app, lifespan
from src.db.connection import engine
from src.db.models import Base
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_blank_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture(scope="session")
async def client():
    with patch("src.main.create_table"):
        async with lifespan(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac
