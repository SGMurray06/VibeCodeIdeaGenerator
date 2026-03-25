from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    euty_experience = Column(String, nullable=False)
    simon_experience = Column(String, nullable=False)
    deep_dive = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
