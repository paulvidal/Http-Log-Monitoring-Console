import time

from datetime import datetime, timedelta
from threading import Thread

from lib import app_config
from lib.app_config import KEY_REFRESH_TIME_S, KEY_LOG_RETENTION_TIME_S


class ClockThread(Thread):

    def __init__(self, generator):
        super().__init__()

        self.daemon = True
        self.refresh_time = app_config.get(KEY_REFRESH_TIME_S)
        self.retention_time = app_config.get(KEY_LOG_RETENTION_TIME_S)
        self.generator = generator

    def run(self):
        current_time = datetime.utcnow()
        previous_time = current_time - timedelta(seconds=self.refresh_time)

        while True:
            current_time = datetime.utcnow()

            self.generator.generate(task_start_time=current_time,
                                    start_interval=previous_time,
                                    end_interval=current_time,
                                    expiry_time=current_time - timedelta(seconds=self.retention_time))

            # Keep track of time at which we started so we do no miss any logs, due to some millisecond error
            # Each log will be in strictly 1 interval
            previous_time = current_time

            time.sleep(self.refresh_time)