"""
this module dispatch the request to backend
"""
import json
from visage.utils.importutils import import_object


class Dispatcher(object):

    def __init__(self, **kwargs):
        """
        :param args: 
        """
        backends = {}

        for key, value in kwargs.items():
            print key
            backends[key] = import_object(value)
        self.backends = backends

    def __call__(self, msg):
        request = json.loads(msg)
        backend_name = request.get('backend')
        method_name = request.get('execute')
        arguments = request.get('arguments')

        backend = self.backends[backend_name]
        method = getattr(backend, method_name)

        resp = method(**arguments)

        return resp

if __name__ == '__main__':

    backends = [
        'visage.backend.test.Test'
    ]

    request = {
        'backend': 'visage.backend.test.Test',
        'execute': 'test',
        'arguments': {
            'args': [],
            'kwargs': {
                'name': 'xxx',
                'id': '123'
            }
        }
    }

    d = Dispatcher(*backends)
    print d(request)
