from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean

from app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    job_id = Column(Integer)

    txn_id = Column(String)

    date = Column(String)

    merchant = Column(String)

    amount = Column(Float)

    currency = Column(String)

    status = Column(String)

    category = Column(String)

    account_id = Column(String)

    is_anomaly = Column(Boolean)

    anomaly_reason = Column(String)