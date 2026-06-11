from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    status = Column(String)

    raw_rows = Column(Integer)

    clean_rows = Column(Integer)

    anomaly_count = Column(Integer)
    summary = Column(String)