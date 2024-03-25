from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from src.conf.config import settings
from src.database.models import Base, User

# SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
