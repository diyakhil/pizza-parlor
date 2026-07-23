# this is the sync session file, used by Celery workers + Alembic
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

from dotenv import load_dotenv

load_dotenv()

SYNC_DATABASE_URL = os.getenv("DATABASE_URL_SYNC")

# one session per task — same isolation guarantee as one-session-per-request,
# just triggered by a Celery task boundary instead of an HTTP request boundary

engine = create_engine(SYNC_DATABASE_URL, echo=True)
SyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def get_db():
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()