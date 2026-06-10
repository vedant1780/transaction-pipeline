from sqlalchemy import *

from app.database import Base

class JobSummary(Base):

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)

    job_id = Column(Integer)

    total_spend_inr = Column(Float)

    total_spend_usd = Column(Float)

    anomaly_count = Column(Integer)

    narrative = Column(Text)

    risk_level = Column(String)