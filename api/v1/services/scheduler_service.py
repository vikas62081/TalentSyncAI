import asyncio
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from api.v1.services.job_service import JobService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService: 
    def __init__(self):
        self.job_service = JobService()
        
        # Create a scheduler instance as an instance variable
        self.scheduler = BackgroundScheduler()
        self.job_running = False 
        
    def add_task(self):
        if self.job_running:
            logger.info("Job is already running. Skipping adding new job for execution.")
            return
        self.scheduler.add_job(self.check_for_update, CronTrigger(hour="*/6"))
        # Start the scheduler
        self.scheduler.start()
        logger.info("\nScheduler started. Fetching data every 6 hours.\n") 
        
        # Executing immediately
        immediate_trigger = os.getenv('SCHEDULER_IMMEDIATE_TRIGGER')=="True" or False
        if immediate_trigger:
            self.check_for_update()
    
    def check_for_update(self):
        if self.job_running:
            logger.info("Job is already running. Skipping new execution.")
            return
        self.job_running = True
        try:
            # Update for off season internship
            asyncio.create_task(self.job_service.process_emails())
            logger.info("Processed all emails successfully.\n")
        except Exception as e: 
            logger.error(f"Error during update check: {str(e)}")
        finally:
            self.job_running = False
            self.shutdown()
            
    def shutdown(self):
        self.scheduler.shutdown()

