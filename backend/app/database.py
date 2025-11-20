from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from supabase import create_client

# Determine database URL
# Priority: Supabase > SQLite
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    # Use Supabase PostgreSQL
    # Convert Supabase URL to SQLAlchemy format
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_KEY
    
    # Extract PostgreSQL connection string from Supabase
    # Format: https://[project-id].supabase.co
    # We need to construct: postgresql://postgres:[password]@[host]:[port]/postgres
    database_url = f"postgresql://postgres:{settings.SUPABASE_SERVICE_ROLE_KEY}@db.{supabase_url.split('//')[1].split('.')[0]}.supabase.co:5432/postgres"
else:
    # Fallback to SQLite for local development
    database_url = settings.DATABASE_URL or "sqlite:///./academic_scheduler.db"

# SQLAlchemy setup for ORM
if database_url.startswith('sqlite'):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    # PostgreSQL connection
    engine = create_engine(database_url, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Supabase client setup (only if credentials are provided)
supabase = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_db():
    """Get SQLAlchemy database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase():
    """Get Supabase client instance"""
    return supabase