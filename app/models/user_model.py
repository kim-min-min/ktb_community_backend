from sqlalchemy import Column, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String(255), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False, unique=True)
    profile_image_path = Column(String(255), nullable=True)
