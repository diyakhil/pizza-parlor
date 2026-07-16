import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# standard "one session per request" pattern
# each incoming request gets its own isolated session, work happens, and cleanup is guaranteed regardless of success or failure 

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session