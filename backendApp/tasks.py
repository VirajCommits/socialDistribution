import threading
import time


def start_github_fetcher_thread():
    from .views import (
        fetch_and_create_github_posts,
    )  # Import here instead of at the top

    def run():
        while True:
            fetch_and_create_github_posts()
            time.sleep(3600)  # Run every hour (3600 seconds)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
