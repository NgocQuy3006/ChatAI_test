
import typing
# Vá lỗi SQLAlchemy cho Python 3.13
if not hasattr(typing, "TypeAliasType"):
    typing.TypeAliasType = type
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được cấu hình trong file .env")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():
    from models import Conversation, Message
    Base.metadata.create_all(bind=engine)
    print(" Database đã được khởi tạo xong.")
