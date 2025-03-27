from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db_user: str = os.getenv("USER")
db_port: int = os.getenv("PORT")
db_host: str = os.getenv("HOST")
db_password: str = os.getenv("PASS")
db_domain: str = os.getenv("DOMAIN")
db_name: str = os.getenv("DB_NAME") 

# Database URL from environment variables
DATABASE_URL: str = f'{db_domain}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
