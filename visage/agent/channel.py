# Qemu agent in Python.
#
# Author: Lizhou Fan <cinuor@gmail.com>
# Last Change: April 20, 2017

"""
This module implements the guest agent.
It runs in KVM or QEMU guests
"""

import json

from visage.common import exception
from visage.utils import log

LOG = log.Log()


class ChannelAgent(object):
    """
    Channel agent listens on a character device 
    and read a request from the device.
    """

    def __init__(self, dispatcher, handle, label):
        """
        init the agent
        
        :param dispatcher: Dispatcher object, 
        :param handle: File object
        :param label: string
        """
        self._dispatcher = dispatcher
        self._handle = handle
        self._label = label

    def _readline(self):
        """
        Read a string from host
        :return: json string
        """
        LOG.debug("begain to read data from %s..." % self._label)
        # here we can check the format of the data,
        # if it is not json string, raise an exception to avoid more works
        data = self._handle.readline().strip()
        LOG.debug("read data: %s" % data)
        return data

    def _write(self, data):
        """
        write data to the host
        :param data: string
        :return: None
        """
        if not data.endswith("\n"):
            data = data + '\n'
        self._handle.write(data)
        self._handle.flush()
        LOG.debug("Write %s to host" % data)

    def get_request(self):
        """
        read from host and handle it
        :return: dict object
        """
        data = self._readline()
        try:
            request = json.loads(data)
            LOG.debug("Parse request %s" % request)
            return request
        except ValueError:
            raise exception.JsonDecodeError("invalid request data")

    def write(self, data):
        """
        :param data: string or dict 
        :return: None
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        elif isinstance(data, str):
            pass
        else:
            raise exception.ResponseValueError
        try:
            self._write(data)
        except IOError:
            raise exception.ResponseError

    def enter_main_loop(self):
        """
        run forever to handle the request
        request:
        {
            "backend": "module_name"
            "execute": "method_name"
            "arguments": {
                "path": "XXXX"
                ...
            }
        }
        :return: response object
        """
        while True:
            try:
                request = self.get_request()
                # make sure that no matter what happend, for example, exception
                # it should return a response too
                resp = self._dispatcher(request)

                # write back to host
                self.write(resp)
            except exception.JsonDecodeError:
                # ocurred when decode json string
                pass
            except exception.ResponseValueError:
                # ocurred when encode dict object
                pass
            except exception.ResponseError:
                # occured when IOError
                pass











