"""
this module dispatch the request to backend
"""

from visage.utils.importutils import import_object

class Dispatcher(object):

    def __init__(self, *args):
        """
        :param args: 
        """
        backends = {}

        for item in args:
            print item
            backends[item] = import_object(item)

        self.backends = backends

    def __call__(self, request):
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
        'arguments': {}
    }

    d = Dispatcher(*backends)
    print d(request)
