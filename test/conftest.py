import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app, lifespan
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture(scope="session")
async def client():
    with patch("src.main.create_table"):
        async with lifespan(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac
