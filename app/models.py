from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base

class Event(Base):
    __tablename__ = 'events'
    id  = Column(Integer, primary_key=True)
    name = Column(String(100))
    location = Column(String(100))
    site_url = Column(String(1000))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)

    def __init__(self, **kwargs):
        self.id  = kwargs.get('id')
        self.name = kwargs.get('name')
        self.location  = kwargs.get('location')
        self.site_url = kwargs.get('site_url')
        self.start_datetime = kwargs.get('start_datetime')
        self.end_datetime = kwargs.get('end_datetime')
