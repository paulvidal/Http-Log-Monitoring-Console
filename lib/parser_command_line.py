import argparse
import sys
import os

from lib import app_config
from lib.app_config import KEY_LOG_RETENTION_TIME_S, KEY_REQUEST_FREQUENCY_PER_S, KEY_REFRESH_TIME_S, KEY_LOG_FILE_PATH


def parse_config():
    """
    Parse the config arguments given to the program, and returns a dictionary for the app config to update itself

    :return: dictionary of config values
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--update", help="update frequency (in s)", type=int)
    parser.add_argument("-r", "--retention", help="time interval to analyse for alerts (in s)", type=int)
    parser.add_argument("-f", "--frequency", help="threshold of requests/s", type=int)
    parser.add_argument("-p", "--path", help="file path to the log file")

    args = parser.parse_args()

    # Check args values
    if args.update and args.update <= 0:
        print('Argument update "-u" or "--update" must be a positive integer')
        sys.exit()

    if args.retention and args.retention <= 0:
        print('Argument retention "-r" or "--retention" must be a positive integer')
        sys.exit()

    if args.frequency and args.frequency <= 0:
        print('Argument frequency "-f" or "--frequency" must be a positive integer')
        sys.exit()

    # Check that the file to parse actually exists
    if args.path and not os.path.exists(args.path):
        print('Argument path "-p" or "--path" must be an existing file')
        sys.exit()

    default_path = app_config.get(KEY_LOG_FILE_PATH)

    if not args.path and not os.path.exists(default_path):
        print('Could no find log file at location: {}'.format(default_path))
        sys.exit()

    return {
        KEY_LOG_RETENTION_TIME_S: args.retention,
        KEY_REQUEST_FREQUENCY_PER_S: args.frequency,
        KEY_REFRESH_TIME_S: args.update,
        KEY_LOG_FILE_PATH: args.path,
    }