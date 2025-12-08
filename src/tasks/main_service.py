from celery_app import celery_app
from helpers.config import get_settings
import logging

# from time import sleep
from datetime import datetime
import asyncio

logger = logging.getLogger("celery.task")


@celery_app.task(bind=True)
def send_email_report(self, mail_wait_seconds: int = 3):
    return asyncio.run(_send_email_report(self, mail_wait_seconds))


async def _send_email_report(task_instance, mail_wait_seconds: int = 3):
    settings = get_settings()
    started_at = str(datetime.now())
    task_instance.update_state(
        state="PROGRESS",
        meta={"status": "Starting to send email reports...", "started_at": started_at},
    )
    for i in range(10):
        logger.info(f"Sending report to user {i+1}")
        await asyncio.sleep(mail_wait_seconds)
    return {
        "status": "Success",
        "message": "Reports sent to all users",
        "started_at": started_at,
        "finished_at": str(datetime.now()),
    }
