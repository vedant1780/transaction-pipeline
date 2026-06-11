# Transaction Processing Pipeline

A scalable transaction processing pipeline built with **FastAPI**, **PostgreSQL**, **Redis**, **Celery**, **Docker**, and **Gemini AI**. The system accepts CSV transaction uploads, processes them asynchronously, detects anomalies, stores results in PostgreSQL, and generates AI-powered summaries.

---

## Features

### CSV Upload
- Upload transaction CSV files
- Validate file format
- Store uploaded files securely

### Data Cleaning
- Standardize date formats
- Normalize transaction amounts
- Handle missing values
- Remove duplicate records

### Anomaly Detection

Detects suspicious transactions using:

**Amount-Based Detection**
- Flags transactions where: `Amount > 3 × Account Median`

**Currency Mismatch Detection**
- Flags transactions where domestic merchants are billed in foreign currency.

> **Example:**
> ```
> Merchant: SWIGGY
> Currency: USD
> ```

### Asynchronous Processing

Uses **Celery** and **Redis** for background processing.

```
Upload CSV
    │
    ▼
FastAPI
    │
    ▼
Redis Queue
    │
    ▼
Celery Worker
    │
    ▼
CSV Processing
    │
    ▼
PostgreSQL
```

### AI-Powered Summary

Uses **Gemini API** to generate:
- Transaction insights
- Spending analysis
- Anomaly summaries
- Category-wise spending overview

> **Example output:**
> ```
> Processed 100 transactions.
> Removed 5 duplicate records.
> Detected 3 anomalies.
> Travel was the highest spending category.
> ```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Database | PostgreSQL |
| Queue | Redis |
| Background Tasks | Celery |
| AI | Gemini |
| Containerization | Docker |
| ORM | SQLAlchemy |
| Data Processing | Pandas |

---

## Project Structure

```
transaction-pipeline/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │
│   ├── models/
│   │   ├── job.py
│   │   └── transactions.py
│   │
│   ├── services/
│   │   ├── csv_processor.py
│   │   ├── anomaly_detection.py
│   │   └── gemini_service.py
│   │
│   ├── tasks/
│   │   └── process_csv.py
│   │
│   ├── database.py
│   ├── celery_app.py
│   └── main.py
│
├── uploads/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/transaction-pipeline.git
cd transaction-pipeline
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/transactions
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Start PostgreSQL

```bash
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  postgres:16
```

### 6. Start Redis

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7
```

Verify:

```bash
docker exec -it redis redis-cli ping
```

Expected output:

```
PONG
```

### 7. Run FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 8. Run Celery Worker

```bash
celery -A app.celery_app:celery_app worker --loglevel=info
```

---

## API Endpoints

### Upload CSV

```
POST /jobs/upload
```

**Response:**

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

**Response:**

```json
{
  "job_id": 1,
  "status": "completed",
  "raw_rows": 100,
  "clean_rows": 95,
  "anomaly_count": 3
}
```

### Get Results

```
GET /jobs/{job_id}/results
```

**Response:**

```json
{
  "job_id": 1,
  "status": "completed",
  "summary": "Processed 100 transactions and detected 3 anomalies.",
  "transactions": [...]
}
```

---

## Processing Workflow

```
CSV Upload
    │
    ▼
FastAPI API
    │
    ▼
Store File
    │
    ▼
Create Pending Job
    │
    ▼
Redis Queue
    │
    ▼
Celery Worker
    │
    ├── Data Cleaning
    ├── Anomaly Detection
    ├── AI Summary Generation
    │
    ▼
PostgreSQL
    │
    ▼
Results API
```

---

## Future Enhancements

- [ ] JWT Authentication
- [ ] Role-Based Access Control
- [ ] Advanced Fraud Detection Models
- [ ] Dashboard & Analytics UI
- [ ] Kafka Integration
- [ ] Batch Processing Support
- [ ] Automated Email Reports

---

## Author

**Vedant Verma**

- GitHub: [github.com/vedant1780](https://github.com/vedant1780)
- LinkedIn: [linkedin.com/in/vedant-verma](https://linkedin.com/in/vedant-verma)

---

## License

This project is licensed under the [MIT License](LICENSE).