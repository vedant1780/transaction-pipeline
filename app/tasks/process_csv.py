from app.celery_app import celery_app
from app.services.csv_processor import load_csv
from app.database import SessionLocal
from app.models.job import Job
from app.models.transactions import Transaction
from app.services.gemini_service import generate_summary

@celery_app.task
def process_csv(filepath, job_id):

    db = SessionLocal()

    try:
        summary = load_csv(filepath)

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            return
        # Generate AI summary
        try:
            summary_text = generate_summary(
                summary["raw_rows"],
                summary["clean_rows"],
                summary["anomalies"],
                summary["category_breakdown"]
            )
        except Exception:
            summary_text = "AI summary temporarily unavailable."

        # Save summary in Job table
        job.summary = summary_text

        # Update job
        job.status = "completed"
        job.raw_rows = summary["raw_rows"]
        job.clean_rows = summary["clean_rows"]
        job.anomaly_count = len(summary["anomalies"])

        # Save transactions
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
                anomaly_reason=(
                    str(txn.get("anomaly_reason"))
                    if txn.get("anomaly_reason")
                    else None
                )
            )

            db.add(transaction)

        db.commit()

    except Exception as e:

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if job:
            job.status = "failed"
            db.commit()

        raise e

    finally:
        db.close()