import argparse
import random
import time
import pytz

from datetime import datetime

HOSTS = [
    '127.0.0.1'
]

NAMES = [
    'john',
    'mary',
    'paul'
]

METHODS = [
    'GET',
    'POST',
    'PUT'
]

URL = [
    '/api/user',
    '/book/1',
    '/book/4',
    '/book/5',
    '/contact/3',
    '/',
    '/cooking/2',
    '/recipes',
    '/cleaning/3'
]

PROTOCOL = [
    'HTTP/1.0',
    'HTTP/1.1',
    'HTTP/2.0'
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="file path to the log file")
    parser.add_argument("-r", "--rate", help="writes per seconds", type=int)
    args = parser.parse_args()

    file_path = args.path if args.path else "/var/log/access.log"
    rate = args.rate if args.rate else 10

    while True:

        with open(file_path, "a") as file:
            time_now = datetime.strftime(datetime.now(pytz.utc), "%d/%b/%Y:%H:%M:%S %z")

            file.write('{} - {} [{}] "{} {} {}" {} {}\n'.format(
                random.choice(HOSTS),
                random.choice(NAMES),
                time_now,
                random.choice(METHODS),
                random.choice(URL),
                random.choice(PROTOCOL),
                random.randint(100, 600),
                random.randint(0, 10000)
            ))

        time.sleep(1 / rate)