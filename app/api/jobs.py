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
from app.models.summary import JobSummary

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

    job = Job(
        filename=file.filename,
        status="pending"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    process_csv.delay(
        filepath,
        job.id
    )

    return {
        "job_id": job.id,
        "status": job.status
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
        "filename": job.filename,
        "status": job.status,
        "row_count_raw": job.row_count_raw,
        "row_count_clean": job.row_count_clean,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "error_message": job.error_message
    }
@router.get("/jobs/{job_id}/results")
def get_results(
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

    summary = (
        db.query(JobSummary)
        .filter(JobSummary.job_id == job_id)
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    return {
        "job": {
            "id": job.id,
            "filename": job.filename,
            "status": job.status
        },

        "summary": {
            "total_spend_inr":
                summary.total_spend_inr
                if summary else None,

            "total_spend_usd":
                summary.total_spend_usd
                if summary else None,

            "top_merchants":
                summary.top_merchants
                if summary else {},

            "anomaly_count":
                summary.anomaly_count
                if summary else 0,

            "risk_level":
                summary.risk_level
                if summary else None,

            "narrative":
                summary.narrative
                if summary else None
        },

        "transactions": [
            {
                "txn_id": t.txn_id,
                "merchant": t.merchant,
                "amount": t.amount,
                "currency": t.currency,
                "category": t.category,
                "account_id": t.account_id,

                "is_anomaly": t.is_anomaly,
                "anomaly_reason": t.anomaly_reason,

                "llm_category": t.llm_category,
                "llm_failed": t.llm_failed
            }
            for t in transactions
        ]
    }