from datetime import datetime

from lib import app_config
from lib.app_config import KEY_LOG_RETENTION_TIME_S


OK_MESSAGE = 'Traffic looking good!'

COLOR_NO_ALERTS = 'VERYGOOD'
COLOR_RECOVERED = 'CAUTIONHL'
COLOR_ALERTS = 'CRITICAL'


class ConsoleModel:

    def __init__(self):
        self.log_retention_time = app_config.get(KEY_LOG_RETENTION_TIME_S)
        self.last_update_time = datetime.utcnow()

        self.previous_alerts = []
        self.current_alerts = []

        self.stats = []
        self.alerts_history = []

    def get_current_alerts(self):
        return self.current_alerts

    def get_previous_alerts(self):
        return self.previous_alerts

    def insert_alert_history(self, alert):
        self.alerts_history.insert(0, alert)

    def update(self, task_time, stats, alerts):
        """
        Method updating the state of the console model with the given stats and alerts.
        2 sets of alerts are recorded, the current alerts and the previous alerts that are no longer valid, which help
        keep track on display of the changes that occurred during this update.
        A history of the alerts is also used to display all the alerts that happened on the screen.

        :param task_time: the datetime at which the update was triggered
        :param stats: the computed statistics object
        :param alerts: the computed alerts objects
        """
        self.last_update_time = task_time
        self.stats = stats

        new_previous_alerts = []
        new_current_alerts = []

        # Check if the current alerts are still valid
        for current_alert in self.current_alerts:
            if current_alert.is_in(alerts):
                new_current_alerts.append(current_alert)
                continue

            # If a current alert is no longer found in the new alert batch, it means it has recovered and is no longer
            # valid, so we create a recovered Alert object that we put in the previous_alerts and in the alert history
            recovered_alert = current_alert.recover(task_time)
            new_previous_alerts.append(recovered_alert)
            self.insert_alert_history(recovered_alert)

        # Add the new detected alerts the the current alerts
        for alert in alerts:
            if not alert.is_in(new_current_alerts):
                new_current_alerts.append(alert)
                self.insert_alert_history(alert)

        self.previous_alerts = new_previous_alerts
        self.current_alerts = new_current_alerts

    def get_alert_status_message(self):
        """
        Method determining the current status to show on the main screen, based on the current alerts and the
        previous alerts

        :return: a message and a color to display on the screen
        """
        if self.current_alerts and self.previous_alerts:
            return '{} alerts detected, {} alerts recovered'\
                       .format(len(self.current_alerts), len(self.previous_alerts)), COLOR_ALERTS

        elif len(self.current_alerts) > 1:
            return '{} alerts detected'.format(len(self.current_alerts)), COLOR_ALERTS

        elif len(self.current_alerts) == 1:
            return self.current_alerts[0], COLOR_ALERTS

        elif len(self.previous_alerts) > 1:
            return '{} alerts recovered'.format(len(self.previous_alerts)), COLOR_RECOVERED

        elif len(self.previous_alerts) == 1:
            return self.previous_alerts[0], COLOR_RECOVERED

        return OK_MESSAGE, COLOR_NO_ALERTS

    def get_last_updated_message(self):
        return '[{}]'.format(self.last_update_time.strftime("%Y-%m-%d %H:%M:%S"))

    def get_stats_messages(self):
        return self.stats

    def get_alert_history_messages(self):
        return self.alerts_history
