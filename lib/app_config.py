"""
A Global configuration for the application, to fetch all the configurable parameters that can be overridable by the user
"""

KEY_REFRESH_TIME_S           = 'KEY_REFRESH_TIME_S'
KEY_REQUEST_FREQUENCY_PER_S  = 'KEY_REQUEST_FREQUENCY_PER_S'
KEY_LOG_RETENTION_TIME_S     = 'KEY_LOG_RETENTION_TIME_S'
KEY_LOG_FILE_PATH            = 'KEY_LOG_FILE_PATH'

_CONFIG = {
    KEY_REFRESH_TIME_S: 10,
    KEY_REQUEST_FREQUENCY_PER_S: 10,
    KEY_LOG_RETENTION_TIME_S: 120,
    KEY_LOG_FILE_PATH: '/var/log/access.log'
}


def get(key):
    return _CONFIG.get(key)


def update(configs):
    for config_key in configs:
        if configs.get(config_key):
            _CONFIG[config_key] = configs[config_key]