from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Создаём движок SQLAlchemy
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

# Сессия для взаимодействия с БД
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
