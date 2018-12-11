from collections import Counter
from math import floor

from lib import app_config
from lib.app_config import KEY_REFRESH_TIME_S

TOP_SECTIONS_COUNT = 5


class Stat:

    def __init__(self, time, message):
        self.time = time
        self.message = message

    def __str__(self):
        return '{}'.format(self.message)


def compute(time, logs):
    stats = []

    if not logs:
        return [Stat(time, 'Currently no traffic')]

    for compute_stat in STAT_COMPUTERS:
        stats += compute_stat(time, logs)

    return stats


def _compute_stat_total_hits(time, logs):
    return [Stat(time, 'Total hits: {}'.format(len(logs)))]


def _compute_hits_per_second(time, logs):
    refresh_time = app_config.get(KEY_REFRESH_TIME_S)
    average_hit_count = round(len(logs) / refresh_time, 1)
    return [Stat(time, 'Average hit count: {}/s'.format(average_hit_count))]


def _compute_stats_sections_with_most_hits(time, logs):
    section_hit_mapping = {}

    for log in logs:
        section_hit = log.get_section_hit()

        if section_hit_mapping.get(section_hit):
            section_hit_mapping[section_hit] += 1
        else:
            section_hit_mapping[section_hit] = 1

    most_hit_sections = dict(Counter(section_hit_mapping).most_common(TOP_SECTIONS_COUNT))
    
    i = 1
    stats = []

    for section in most_hit_sections:
        stats.append(Stat(time, 'Most hit section {}: {} ({})'.format(i, section, most_hit_sections[section])))
        i += 1

    return stats


def _compute_stats_response_codes(time, logs):
    code_type_count_mapping = {}

    for log in logs:
        code_type = log.get_response_code_type_formatted()

        if code_type_count_mapping.get(code_type):
            code_type_count_mapping[code_type] += 1
        else:
            code_type_count_mapping[code_type] = 1

    return [Stat(time, '{} count: {}'.format(code_type, code_type_count_mapping[code_type]))
            for code_type in sorted(code_type_count_mapping)]


def _compute_stat_bytes_sent(time, logs):
    total_bytes = sum([log.bytes for log in logs])
    return [Stat(time, 'Total bytes transfered: {}'.format(total_bytes))]


STAT_COMPUTERS = [
    _compute_stat_total_hits,
    _compute_hits_per_second,
    _compute_stats_sections_with_most_hits,
    _compute_stats_response_codes,
    _compute_stat_bytes_sent
]