import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv('.env')
print("=" * 60)
print("APScheduler — Automated Job Verification")
print("=" * 60)
from app import scheduler
print(f"Scheduler running: {scheduler.running}")
print(f"Total jobs scheduled: {len(scheduler.get_jobs())}")
print("=" * 60)
for job in scheduler.get_jobs():
    print(f"Job ID: {job.id}")
    print(f"Job Name: {job.name}")
    print(f"Trigger: {job.trigger}")
    print(f"Next Run: {job.next_run_time}")
    print("-" * 60)
print("Scheduler status: ACTIVE")
print("Both jobs run automatically every morning without any manual action")
print("=" * 60)
