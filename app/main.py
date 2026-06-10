from fastapi import FastAPI
from app.api.jobs import router
from app.database import Base
from app.database import engine
from app.models.job import Job
from app.models.transactions import Transaction
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Transaction Pipeline API"
    }


app.include_router(router)