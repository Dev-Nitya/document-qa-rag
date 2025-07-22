from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.now())

    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey('chat_sessions.id'))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now())
    run_id = Column(String, nullable=True)  # Optional run_id for tracking

    session = relationship("ChatSession", back_populates="messages")

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey('chat_sessions.id'))
    question = Column(Text)
    answer = Column(Text)
    feedback = Column(String)  # "thumbs_up" or "thumbs_down"
    comment = Column(Text, default="")
    run_id = Column(String, nullable=True)  # Optional run_id for tracking