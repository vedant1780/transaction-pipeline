from celery import Celery
from dotenv import load_dotenv
load_dotenv()
import os
REDIS_URL=os.getenv("REDIS_URL")
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.imports = (
    "app.tasks.process_csv",
)