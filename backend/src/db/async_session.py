#this is the async session file for the fast api application.
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

#commit is what pushes the changes to the DB, happens at the end of every async session, rollback undoes the change if error is thrown
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise