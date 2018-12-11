from threading import Thread

from lib import stats, alerts, console


class MonitorThreadGenerator:
    def __init__(self, log_queue, console_model):
        self.log_queue = log_queue
        self.console_model = console_model

    def generate(self, task_start_time, start_interval, end_interval, expiry_time):
        """
        Main function called to spawn Monitor threads

        :param task_start_time: task start datetime
        :param start_interval: start datetime for logs to process
        :param end_interval: end datetime for logs to process
        :param expiry_time: datetime under which logs are considered expired
        """
        monitor = Monitor(self.log_queue, self.console_model, task_start_time, start_interval, end_interval, expiry_time)
        Thread(target=monitor.run).run()


class Monitor:
    def __init__(self, log_queue, console_model, task_start_time, start_interval_time, end_interval_time, expiry_time):
        super().__init__()

        self.log_queue = log_queue
        self.console_model = console_model
        self.task_start_time = task_start_time
        self.start_interval_time = start_interval_time
        self.end_interval_time = end_interval_time
        self.expiry_time = expiry_time

    def run(self):
        """
        Main task for the monitoring thread, which is responsible for respectively
        - flushing the outdated elements out of the queue
        - computing the stats and alerts for the logs in the time interval given to the process
        - updating the console model with those computed stats and alerts
        """
        self._flush_expired_logs()

        computed_stats = self._compute_stats()
        computed_alerts = self._compute_alerts()

        self._update_console(computed_stats, computed_alerts)

    def _flush_expired_logs(self):
        self.log_queue.flush_expired(self.expiry_time)

    def _compute_stats(self):
        logs_in_interval = self.log_queue.get_logs(self.start_interval_time, self.end_interval_time)
        computed_stats = stats.compute(self.task_start_time, logs_in_interval)

        return computed_stats

    def _compute_alerts(self):
        all_logs = self.log_queue.get_all_logs()
        computed_alerts = alerts.compute(self.task_start_time, all_logs)
        return computed_alerts

    def _update_console(self, computed_stats, computed_alerts):
        self.console_model.update(self.task_start_time, computed_stats, computed_alerts)