from sqlalchemy import Column, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class BitcoinPrice(Base):
    __tablename__ = "BitcoinPrice"
    
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    dateAdd = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False) 