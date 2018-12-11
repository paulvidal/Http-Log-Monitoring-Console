from math import floor

from lib import app_config
from lib.app_config import KEY_REQUEST_FREQUENCY_PER_S, KEY_LOG_RETENTION_TIME_S

TYPE_HIGH_TRAFFIC = 'high_traffic_type'


class Alert:

    def __init__(self, time, type, message, recovered=False):
        self.time = time
        self.type = type
        self.message = message
        self.recovered = recovered

    def is_in(self, alerts):
        return any([self.is_same_alert(alert) for alert in alerts])

    def is_same_alert(self, alert):
        return self.type == alert.type

    def recover(self, recover_time):
        """
        Create an alert which represents the recovery, also displayed on the screen

        :return: an Alert with recovered parameter set to True
        """
        return Alert(recover_time, self.type, 'Recovered "{}"'.format(self.message), recovered=True)

    def __str__(self):
        return '[{}] {}'.format(self.time.strftime("%Y-%m-%d %H:%M:%S"), self.message)


def compute(time, logs):
    alerts = []

    for compute_alert in ALERT_COMPUTERS:
        alerts += compute_alert(time, logs)

    return alerts


def compute_alert_high_traffic(time, logs):
    """
    Detect if high traffic by averaging the number of requests over the retention period and detecting if it is smaller
    than the threshold of requests tolerated per minutes

    :param time: the time at which the update task started
    :param logs: a list of all the logs retained
    :return: an alert if high traffic is detected, else None
    """
    retention_time = app_config.get(KEY_LOG_RETENTION_TIME_S)
    request_frequency_per_second = app_config.get(KEY_REQUEST_FREQUENCY_PER_S)

    average_hits_count = floor(len(logs) / retention_time)

    if average_hits_count < request_frequency_per_second:
        return []

    return [Alert(time, TYPE_HIGH_TRAFFIC, 'High traffic - {} hits/s'.format(average_hits_count))]


ALERT_COMPUTERS = [
    compute_alert_high_traffic
]