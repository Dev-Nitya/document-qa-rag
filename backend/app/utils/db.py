from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.chat import Base

engine = create_engine("sqlite:///./chat.db")
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)