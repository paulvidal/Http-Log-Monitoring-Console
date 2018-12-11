import unittest
from datetime import datetime, timedelta

from lib import app_config, alerts
from lib.app_config import KEY_REQUEST_FREQUENCY_PER_S, KEY_LOG_RETENTION_TIME_S
from lib.console import ConsoleModel
from lib.log import Log
from lib.log_queue import LogQueue
from lib.monitor import Monitor


class AlertsTest(unittest.TestCase):

    def setUp(self):
        self.console_model = ConsoleModel()
        self.log_queue = LogQueue()

        self.request_frequency_per_s = 5
        self.log_retention_time_s = 10

        # Setup the configuration
        app_config.update({
            KEY_REQUEST_FREQUENCY_PER_S: self.request_frequency_per_s,
            KEY_LOG_RETENTION_TIME_S: self.log_retention_time_s
        })

    def _create_monitor(self, count, time_delta_s):
        """
        Helper adding logs to the log_queue for a set date (+ offset :time_delta_s: if required), and creating a Monitor
        object that will run for an interval [start_interval_time, end_interval_time] containing the logs such that
        start_interval_time < log_time < end_interval_time

        :param count: number of logs to be generated for the time interval
        :param time_delta_s: offset time in seconds at which logs are generated, useful when multiple executions
        :return: a Monitor ready to run and process the logs in the log_queue for the specified time interval
        """
        date = datetime(year=2018, month=12, day=12, hour=0, minute=0, second=0) + timedelta(seconds=time_delta_s)
        self._generate_logs(count=count, date=date)

        task_start_time = date + timedelta(seconds=1)
        start_interval_time = date - timedelta(seconds=1)
        end_interval_time = date + timedelta(seconds=1)
        expiry_time = date - timedelta(seconds=self.log_retention_time_s)

        return Monitor(self.log_queue, self.console_model, task_start_time, start_interval_time,
                       end_interval_time, expiry_time)

    def _generate_logs(self, count, date, remote_host='127.0.0.1', auth_user='paul', request_verb='GET',
                       resource='/book/1', protocol='HTTP/1.0', status=200, bytes=20):
        """
        Helper generating a number of logs at a given date and adding them to the log log_queue

        :param count: number of logs to generate
        :param date: time at which logs will be generated
        """
        for _ in range(count):
            self.log_queue.append(Log(remote_host, auth_user, date, request_verb, resource, protocol, status, bytes))

    def test_sending_less_logs_than_threshold_should_not_trigger_an_alert(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s - 1  # normal
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_alert_history_messages()), 0)
        self.assertEqual(len(self.console_model.get_current_alerts()), 0)
        self.assertEqual(len(self.console_model.get_previous_alerts()), 0)

    def test_sending_more_logs_than_threshold_should_trigger_an_alert(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1  # spike
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_alert_history_messages()), 1)
        self.assertEqual(len(self.console_model.get_current_alerts()), 1)
        self.assertEqual(len(self.console_model.get_previous_alerts()), 0)

    def test_sending_more_logs_than_threshold_should_trigger_a_high_traffic_alert(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)

        # When
        monitor.run()

        # Then
        alert = self.console_model.get_current_alerts()[0]
        self.assertEqual(alert.type, alerts.TYPE_HIGH_TRAFFIC)
        self.assertFalse(alert.recovered)

    def test_sending_more_logs_than_threshold_but_recovering_after_should_clear_alert(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s - 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_current_alerts()), 0)

    def test_sending_more_logs_than_threshold_but_recovering_after_should_create_recovered_alert(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s - 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_previous_alerts()), 1)

        alert = self.console_model.get_previous_alerts()[0]
        self.assertEqual(alert.type, alerts.TYPE_HIGH_TRAFFIC)
        self.assertTrue(alert.recovered)

    def test_sending_more_logs_than_threshold_but_recovering_after_should_create_2_alerts_in_history(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s - 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_alert_history_messages()), 2)

    def test_going_multiple_time_above_threshold_within_same_retention_timeframe_does_not_trigger_multiple_alarms(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s - 1)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_alert_history_messages()), 1)
        self.assertEqual(len(self.console_model.get_current_alerts()), 1)
        self.assertEqual(len(self.console_model.get_previous_alerts()), 0)

    def test_going_multiple_time_above_threshold_within_different_retention_timeframe_triggers_multiple_alarms(self):
        # Given
        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1  # spike
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=0)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s - 1  # recovery
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s + 10)
        monitor.run()

        log_to_generate_count = self.request_frequency_per_s * self.log_retention_time_s + 1  # spike
        monitor = self._create_monitor(log_to_generate_count, time_delta_s=self.log_retention_time_s + 10)

        # When
        monitor.run()

        # Then
        self.assertEqual(len(self.console_model.get_alert_history_messages()), 3)
        self.assertEqual(len(self.console_model.get_current_alerts()), 1)
        self.assertEqual(len(self.console_model.get_previous_alerts()), 0)