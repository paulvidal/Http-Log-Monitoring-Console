import collections


class LogQueue:
    def __init__(self):
        self.deque = collections.deque()  # Use a deque to store the logs, as it is a concurrent object

    def append(self, log):
        self.deque.append(log)

    def flush_expired(self, expiry_time):
        """
        Remove starting from the front the outdated logs. As logs are appended in chronological order, once we have
        found a log not expired, we stop removing elements.

        :param expiry_time: datetime representing the time under which a log is considered expired
        """
        while len(self.deque) > 0:
            log = self.deque[0]

            if not log.is_expired(expiry_time):
                break

            self.deque.popleft()

    def get_all_logs(self):
        return list(self.deque)

    def get_logs(self, start_interval_time, end_interval_time):
        """
        Get all logs between an interval of time. Logs equal to start time are taken into account but not those equal
        to end time, in order to not take into account twice a log

        :param start_interval_time: start datetime
        :param end_interval_time: end datetime
        :return: all the log objects with a time between these 2 times
        """
        recent_logs = []

        for log in self.get_all_logs():
            if log.is_in_interval(start_interval_time, end_interval_time):
                recent_logs.append(log)

        return recent_logs
