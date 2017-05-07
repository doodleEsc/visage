import functools


def wrap_exception():

    def inner(f):
        @functools.wraps(f)
        def wrapped(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                # TODO check error type, and return error response
                pass
        return wrapped
    return inner