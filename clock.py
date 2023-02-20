from apscheduler.schedulers.blocking import BlockingScheduler
import os

def job():
    os.system('python tweet2sheet.py')

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=30)
    scheduler.start()