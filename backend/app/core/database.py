from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_user = os.getenv("USER")
db_port = os.getenv("PORT")
db_host = os.getenv("HOST")
db_password = os.getenv("PASS")
db_domain = os.getenv("DOMAIN")
db_name = os.getenv("DB_NAME")

# Database URLs
ASYNC_DATABASE_URL = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
SYNC_DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create SQLAlchemy engines
async_engine = create_async_engine(ASYNC_DATABASE_URL,echo=True,pool_size=10,max_overflow=20,pool_pre_ping=True)

sync_engine = create_engine(SYNC_DATABASE_URL,echo=True,pool_size=10,max_overflow=20,pool_pre_ping=True)

# Session makers
AsyncSessionLocal = sessionmaker(bind=async_engine,class_=AsyncSession,expire_on_commit=False,autoflush=False)

SyncSessionLocal = sessionmaker(bind=sync_engine,autocommit=False,autoflush=False)

Base = declarative_base()

# Dependency to get async DB session
async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()

# Dependency to get sync DB session (for operations that don't support async)
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()