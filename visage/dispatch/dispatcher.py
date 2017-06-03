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
            backends[key] = import_object(value)
        self.backends = backends

    def __call__(self, msg):
        request = json.loads(msg)
        backend_name = request.get('backend')
        method_name = request.get('execute')
        args = request.get('args')
        kwargs = request.get('kwargs')

        backend = self.backends[backend_name]
        method = getattr(backend, method_name)

        resp = method(*args, **kwargs)

        return resp

if __name__ == '__main__':

    backends = {
        'Test': 'visage.backend.test.Test'
    }
    j = {
        'backend': 'Test',
        'execute': 'test',
        'args': [],
        'kwargs': {
            'name': 'xxx',
            'id': '123'
        }
    }

    request = json.dumps(j)

    d = Dispatcher(**backends)
    print d(request)
