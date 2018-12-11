import re
import time
from datetime import datetime
from threading import Thread

from lib import app_config
from lib.app_config import KEY_LOG_FILE_PATH
from lib.log import Log

LOG_REGEX = '(.*?) - (.*?) \[(.*?)] \"(.*) (\/.*) (HTTP.*)\" (.*) (.*)'


class ParserThread(Thread):

    def __init__(self, log_queue):
        super().__init__()

        self.daemon = True
        self.file_path = app_config.get(KEY_LOG_FILE_PATH)
        self.log_queue = log_queue

    def run(self):
        """
        Main method of the parsing thread which continuously read from the log file and append the newly parsed line
        info to the log log_queue
        """
        new_lines = self._read_new_lines()

        for line in new_lines:
            parsed_line = self._parse_log_line(line)

            if parsed_line:
                remote_host, auth_user, date, request_verb, resource, protocol, status, bytes = parsed_line
                log = Log(remote_host, auth_user, date, request_verb, resource, protocol, status, bytes)
                self.log_queue.append(log)

    def _read_new_lines(self):
        """
        A generator that never stops reading the file opened, continuously reading where it left of

        :return: yields new line added to the log file
        """
        file = open(self.file_path, "r")

        while True:
            line = file.readline()

            if not line:
                continue

            yield line

    def _parse_log_line(self, line):
        """
        A simple method parsing the log line extracted using regex

        :param line: string representing the line extracted from the log file
        :return: a tuple of elements extracted from the line
        """
        match = re.match(LOG_REGEX, line)

        if not match:
            return None

        remote_host, auth_user, date, request_verb, resource, http_version, status, bytes =  match.groups()

        # We assume logs will always be UTC time
        parsed_date = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S %z").replace(tzinfo=None)
        parsed_status = int(status)
        parsed_bytes = int(bytes)

        return remote_host, auth_user, parsed_date, request_verb, resource, http_version, parsed_status, parsed_bytes