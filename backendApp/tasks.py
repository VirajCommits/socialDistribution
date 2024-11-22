# from apscheduler.schedulers.background import BackgroundScheduler
# import atexit


# def start_scheduler():
#     def job():
#         # Import inside the job to avoid circular imports
#         from .views import fetch_and_create_github_posts

#         fetch_and_create_github_posts()

#     scheduler = BackgroundScheduler()
#     scheduler.add_job(job, "interval", minutes=1)
#     scheduler.start()

#     # Ensure scheduler shuts down gracefully
#     atexit.register(lambda: scheduler.shutdown(wait=False))
