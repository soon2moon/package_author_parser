import time
import functools

def store_timing(location):
    def apply_timing(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            setattr(self, location, duration)
            return result

        return wrap

    return apply_timing