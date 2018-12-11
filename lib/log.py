RESPONSE_CODE_INFORMATIONAL = 100
RESPONSE_CODE_SUCCESS = 200
RESPONSE_CODE_REDIRECTION = 300
RESPONSE_CODE_CLIENT_ERROR = 400
RESPONSE_CODE_SERVER_ERROR = 500


class Log:

    def __init__(self, remote_host, auth_user, date, request_verb, resource, protocol, status, bytes):
        self.remote_host = remote_host
        self.auth_user = auth_user
        self.date = date
        self.request_verb = request_verb
        self.resource = resource
        self.protocol = protocol
        self.status = status
        self.bytes = bytes

    def is_expired(self, expiry_time):
        return self.date <= expiry_time

    def is_in_interval(self, start_interval_time, end_interval_time):
        return start_interval_time <= self.date < end_interval_time

    def get_section_hit(self):
        return '/{}'.format(self.resource.split('/')[1])  # A section is defined as being what's before the second '/'

    def get_response_code_type(self):
        if RESPONSE_CODE_INFORMATIONAL <= self.status <  RESPONSE_CODE_SUCCESS:
            return RESPONSE_CODE_INFORMATIONAL

        elif RESPONSE_CODE_SUCCESS <= self.status <  RESPONSE_CODE_REDIRECTION:
            return RESPONSE_CODE_SUCCESS

        elif RESPONSE_CODE_REDIRECTION <= self.status < RESPONSE_CODE_CLIENT_ERROR:
            return RESPONSE_CODE_REDIRECTION

        elif RESPONSE_CODE_CLIENT_ERROR <= self.status < RESPONSE_CODE_SERVER_ERROR:
            return RESPONSE_CODE_CLIENT_ERROR

        elif RESPONSE_CODE_SERVER_ERROR <= self.status:
            return RESPONSE_CODE_SERVER_ERROR

    def get_response_code_type_formatted(self):
        code_type = self.get_response_code_type()
        return str(code_type).replace('0', 'x')

    def __str__(self):
        return '{} - {} [{}] "{} {} {}" {} {}'.format(self.remote_host,
                                                      self.auth_user,
                                                      str(self.date),
                                                      self.request_verb,
                                                      self.resource,
                                                      self.protocol,
                                                      str(self.status),
                                                      str(self.bytes))