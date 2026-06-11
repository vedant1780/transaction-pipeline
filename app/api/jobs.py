from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
import os
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.store import jobs
from fastapi import HTTPException
import uuid
from app.services.csv_processor import load_csv
from app.models.transactions import Transaction
from app.tasks.process_csv import process_csv

router = APIRouter()
@router.post("/jobs/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files allowed"
        )

    UPLOAD_DIR = "uploads"

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filepath = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Create pending job
    job = Job(
        filename=file.filename,
        status="pending"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue background task
    process_csv.delay(
        filepath,
        job.id
    )

    return {
        "job_id": job.id,
        "status": "pending"
    }
@router.get("/jobs/{job_id}/status")
def get_status(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "raw_rows": job.raw_rows,
        "clean_rows": job.clean_rows,
        "anomaly_count": job.anomaly_count,
        "summary": job.summary,
    }
@router.get("/jobs/{job_id}/results")
def get_results(
    job_id: int,
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    if not transactions:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job_id,
        "transaction_count": len(transactions),
        "transactions": [
            {
                "txn_id": t.txn_id,
                "merchant": t.merchant,
                "amount": t.amount,
                "category": t.category,
                "is_anomaly": t.is_anomaly,
                "anomaly_reason": t.anomaly_reason
            }
            for t in transactions
        ]
    }

   