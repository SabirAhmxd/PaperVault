from database import Base
from sqlalchemy import Column,Integer ,String,Boolean

class Paper(Base):
    __tablename__ = "papers"

    id=Column(Integer,primary_key=True,index=True)
    title = Column(String)
    author= Column(String)
    abstract = Column(String)
    year= Column(Integer)
    reading_status=Column(String)

    
