from celery import Celery
from dotenv import load_dotenv
import os
load_dotenv()
celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL")
)