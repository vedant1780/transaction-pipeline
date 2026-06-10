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

    filepath = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(filepath, "wb") as f:
        f.write(await file.read())
    summary = load_csv(filepath)
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
    "status": "completed",
    "filename": file.filename,
    "raw_rows": summary["raw_rows"],
    "clean_rows": summary["clean_rows"],
    "anomaly_count": len(summary["anomalies"]),
    "anomalies": summary["anomalies"],
    "transactions": summary["data"],
    "category_breakdown": summary["category_breakdown"]
}
    job = Job(
    filename=file.filename,
    status="completed",
    raw_rows=summary["raw_rows"],
    clean_rows=summary["clean_rows"],
    anomaly_count=len(summary["anomalies"])
)

    db.add(job)
    db.commit()
    db.refresh(job)
    for txn in summary["data"]:

        transaction = Transaction(
            job_id=job.id,
            txn_id=str(txn.get("txn_id")),
            date=str(txn.get("date")),
            merchant=str(txn.get("merchant")),
            amount=float(txn.get("amount"))
                if txn.get("amount") is not None
                else 0,
            currency=str(txn.get("currency")),
            status=str(txn.get("status")),
            category=str(txn.get("category")),
            account_id=str(txn.get("account_id")),
            is_anomaly=bool(txn.get("is_anomaly")),
            anomaly_reason=str(txn.get("anomaly_reason"))
                if txn.get("anomaly_reason")
                else None
        )

        db.add(transaction)

    db.commit()

    return jobs[job_id] | {
        "job_id": job_id,
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
        "status": job.status,
        "raw_rows": job.raw_rows,
        "clean_rows": job.clean_rows,
        "anomaly_count": job.anomaly_count
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

   