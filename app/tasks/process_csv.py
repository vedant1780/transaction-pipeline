from datetime import datetime

from app.celery_app import celery_app
from app.services.csv_processor import load_csv
from app.database import SessionLocal

from app.models.job import Job
from app.models.transactions import Transaction
from app.models.summary import JobSummary

from app.services.gemini_service import (
    generate_summary
)


@celery_app.task
def process_csv(
    filepath,
    job_id
):

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

        # -------------------------
        # AI Summary
        # -------------------------

        try:

            summary_text = generate_summary(
                summary["raw_rows"],
                summary["clean_rows"],
                summary["anomalies"],
                summary["category_breakdown"]
            )

        except Exception:

            summary_text = (
                "AI summary temporarily unavailable."
            )

        # -------------------------
        # Risk Level
        # -------------------------

        anomaly_count = len(
            summary["anomalies"]
        )

        if anomaly_count == 0:

            risk_level = "LOW"

        elif anomaly_count <= 5:

            risk_level = "MEDIUM"

        else:

            risk_level = "HIGH"

        # -------------------------
        # Update Job
        # -------------------------

        job.status = "completed"

        job.row_count_raw = (
            summary["raw_rows"]
        )

        job.row_count_clean = (
            summary["clean_rows"]
        )

        job.completed_at = (
            datetime.utcnow()
        )

        # -------------------------
        # Save Job Summary
        # -------------------------

        job_summary = JobSummary(
            job_id=job.id,

            total_spend_inr=
            summary["total_spend_inr"],

            total_spend_usd=
            summary["total_spend_usd"],

            top_merchants=
            summary["top_merchants"],

            anomaly_count=
            anomaly_count,

            narrative=
            summary_text,

            risk_level=
            risk_level
        )

        db.add(job_summary)

        # -------------------------
        # Save Transactions
        # -------------------------

        for txn in summary["data"]:

            transaction = Transaction(

                job_id=job.id,

                txn_id=str(
                    txn.get("txn_id")
                ),

                date=str(
                    txn.get("date")
                ),

                merchant=str(
                    txn.get("merchant")
                ),

                amount=float(
                    txn.get("amount")
                )
                if txn.get("amount")
                is not None
                else 0,

                currency=str(
                    txn.get("currency")
                ),

                status=str(
                    txn.get("status")
                ),

                category=str(
                    txn.get("category")
                ),

                account_id=str(
                    txn.get("account_id")
                ),

                is_anomaly=bool(
                    txn.get(
                        "is_anomaly"
                    )
                ),

                anomaly_reason=
                txn.get(
                    "anomaly_reason"
                ),

                llm_category=
                txn.get(
                    "llm_category"
                ),

                llm_raw_response=
                txn.get(
                    "llm_raw_response"
                ),

                llm_failed=
                txn.get(
                    "llm_failed",
                    False
                )
            )

            db.add(
                transaction
            )

        db.commit()

    except Exception as e:

        job = (
            db.query(Job)
            .filter(
                Job.id == job_id
            )
            .first()
        )

        if job:

            job.status = "failed"

            job.error_message = (
                str(e)
            )

            db.commit()

        raise e

    finally:

        db.close()