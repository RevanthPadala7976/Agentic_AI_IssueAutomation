from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "CRITICAL: DATABASE_URL is not set in environment or .env file! "
        "Please copy .env.example to .env and set your connection string."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class IssueModel(Base):
    __tablename__ = "issues"
    # primary key internal database Row ID
    id = Column(Integer, primary_key=True, index=True)

    # GitHub-issue specific metadata
    number = Column(Integer, unique=True, nullable=False, index=True) # 367830
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    state = Column(String, nullable=False) # closed or open

    # Timestamp indexed for 80/20 split chronological split
    created_at = Column(DateTime, nullable=False, index=True)
    closed_at = Column(DateTime, nullable=True)

    # Labels stored directly as JSON array (e.g. ["bug", "core"])
    labels = Column(JSON, nullable=False, default=[])

def init_db():
    """Create all table defined in Base metadata in PostgreSQL"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("PostgreSQL table initialized successfully!")

