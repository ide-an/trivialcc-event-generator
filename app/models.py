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

    def __repr__(self):
        return f"Event(id  = {self.id!r}, name = {self.name!r}, location = {self.location!r}, site_url = {self.site_url!r}, start_datetime = {self.start_datetime!r}, end_datetime = {self.end_datetime!r})"
