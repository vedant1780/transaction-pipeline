# Transaction Processing Pipeline

A scalable transaction processing pipeline built with **FastAPI**, **PostgreSQL**, **Redis**, **Celery**, **Docker**, and **Gemini AI**. The system accepts CSV transaction uploads, processes them asynchronously, detects anomalies, stores results in PostgreSQL, and generates AI-powered financial summaries.

---

## Features

### CSV Upload & Validation
- Upload transaction CSV files
- Validate file format and structure
- Store uploaded files securely
- Create asynchronous processing jobs

### Data Cleaning & Normalization
- Standardize date formats
- Normalize currency values
- Handle missing data
- Remove duplicate transactions
- Normalize transaction status and categories

### Anomaly Detection

Detects suspicious transactions using rule-based checks:

**Amount-Based Detection**
Flags transactions where: `Amount > 3 × Account Median`

**Currency Mismatch Detection**
Flags transactions where domestic merchants are billed in USD.

Example:
```
Merchant: SWIGGY
Currency: USD
```

### Asynchronous Processing

Uses Celery workers and Redis queues to process uploaded files in the background.

```
CSV Upload → FastAPI → Redis Queue → Celery Worker → Processing Pipeline → PostgreSQL
```

### AI-Powered Financial Summary

Uses Gemini AI to generate:
- Spending insights
- Transaction summaries
- Risk assessment
- Category-wise analysis
- Anomaly observations

### Analytics

Calculates:
- Total INR spend
- Total USD spend
- Top merchants
- Anomaly count
- Risk level

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Database | PostgreSQL |
| Queue Broker | Redis |
| Background Tasks | Celery |
| ORM | SQLAlchemy |
| Data Processing | Pandas |
| AI Summary | Gemini 2.5 Flash |
| Containerization | Docker |
| API Documentation | Swagger UI |

---

## Database Schema

### Job
Tracks uploaded files and processing status.

| Column | Description |
|---|---|
| id | Primary key |
| filename | Uploaded CSV filename |
| status | Job status (pending/processing/completed/failed) |
| row_count_raw | Total rows in uploaded CSV |
| row_count_clean | Rows after cleaning |
| created_at | Job creation timestamp |
| completed_at | Job completion timestamp |
| error_message | Error details if failed |

### Transaction
Stores processed transaction records.

| Column | Description |
|---|---|
| id | Primary key |
| job_id | Foreign key to Job |
| txn_id | Transaction identifier |
| date | Transaction date |
| merchant | Merchant name |
| amount | Transaction amount |
| currency | Transaction currency |
| status | Transaction status |
| category | Transaction category |
| account_id | Account identifier |
| is_anomaly | Anomaly flag |
| anomaly_reason | Reason for anomaly flag |
| llm_category | AI-assigned category |
| llm_raw_response | Raw LLM response |
| llm_failed | LLM processing failure flag |

### JobSummary
Stores aggregated analytics and AI-generated insights.

| Column | Description |
|---|---|
| id | Primary key |
| job_id | Foreign key to Job |
| total_spend_inr | Total INR spend |
| total_spend_usd | Total USD spend |
| top_merchants | Top merchants list |
| anomaly_count | Total anomalies detected |
| narrative | AI-generated narrative summary |
| risk_level | Assessed risk level |

---

## Project Structure

```
transaction-pipeline/
├── app/
│   ├── api/
│   │   └── jobs.py
│   ├── models/
│   │   ├── job.py
│   │   ├── transactions.py
│   │   └── job_summary.py
│   ├── services/
│   │   ├── csv_processor.py
│   │   ├── anomaly_detection.py
│   │   └── gemini_service.py
│   ├── tasks/
│   │   └── process_csv.py
│   ├── database.py
│   ├── celery_app.py
│   └── main.py
├── uploads/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres@postgres:5432/transactions
REDIS_URL=redis://redis:6379/0
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=transactions
GEMINI_API_KEY=your_gemini_api_key
```

---

## Running with Docker

### Build and Start Services
```bash
docker compose up --build
```

### Start in Detached Mode
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

---

## Services

| Service | URL / Port |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | Port 5432 |
| Redis | Port 6379 |

---

## API Endpoints

### Upload CSV
```
POST /jobs/upload
```

Response:
```json
{
  "job_id": 1,
  "status": "pending"
}
```

### Check Job Status
```
GET /jobs/{job_id}/status
```

Response:
```json
{
  "job_id": 1,
  "status": "completed",
  "row_count_raw": 100,
  "row_count_clean": 95
}
```

### Get Processed Results
```
GET /jobs/{job_id}/results
```

Returns all processed transactions for the specified job.

---

## Processing Workflow

```
User Uploads CSV
       ↓
FastAPI Upload Endpoint
       ↓
Store CSV in uploads/
       ↓
Create Job (Pending)
       ↓
Push Task to Redis
       ↓
Celery Worker Consumes Task
       ↓
CSV Cleaning & Validation
       ↓
Anomaly Detection
       ↓
Analytics Generation
       ↓
Gemini AI Summary
       ↓
Store Transactions
       ↓
Store JobSummary
       ↓
Update Job Status
       ↓
Results Available via API
```

---



## Author

**Vedant Verma**

- GitHub: [github.com/vedant1780](https://github.com/vedant1780)
- LinkedIn: [linkedin.com/in/vedant-verma](https://linkedin.com/in/vedant-verma)

---

## License

This project is licensed under the [MIT License](LICENSE).
