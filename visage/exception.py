"""
visage exception module
"""

import json

class VisageException(Exception):
    """
    base visage exception
    """

    msg_fmt = "An unknown exception occurred."

    def __init__(self, message=None):
        if not message:
            message = self.msg_fmt
        self.message = message

        super(VisageException, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full NovaException message, (see __init__)
        return self.args[0]

class JsonDecodeError(VisageException):
    msg_fmt = "Fail to decode the string."


class JsonEncodeError(VisageException):
    msg_fmt = "Fail to encode the object."


class ResponseValueError(VisageException):
    msg_fmt = "Unsupported response type."


class ResponseError(VisageException):
    msg_fmt = "Fail to response"
