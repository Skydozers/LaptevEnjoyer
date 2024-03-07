from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL = 'postgresql://postgres:password@database/Sypchenko'

engine = create_engine(URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ClientDB(Base):
    __tablename__ = 'banking_sypchenko'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Float, nullable=False)