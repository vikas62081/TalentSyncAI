import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from services.job_service import JobService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize JobService
job_service = JobService()

class SchedulerService:
    def __init__(self):
        # Check environment variables for immediate trigger and interval
        immediate_trigger = os.getenv('SCHEDULER_IMMEDIATE_TRIGGER', "False").lower() == "True"
        scheduler_interval_minutes = int(os.getenv('SCHEDULER_INTERVAL_MINUTES', 10))
        
        # Create a scheduler instance
        self.scheduler = BackgroundScheduler()

        # Schedule the job to run at specified intervals
        self.scheduler.add_job(self.check_for_update, 'interval', minutes=scheduler_interval_minutes)

        # Start the scheduler
        self.scheduler.start()
        logger.info(f"Scheduler started. Fetching data every {scheduler_interval_minutes} minutes.")

        # Execute immediately if configured
        if immediate_trigger:
            logger.info("Immediate execution triggered.")
            self.check_for_update()

    def check_for_update(self):
        try:
            logger.info("Checking for updates...")
            result = job_service.process_emails()
            logger.info(f"Update check completed successfully. Result: {result}")
        except Exception as e:
            logger.error(f"Error during update check: {str(e)}")

