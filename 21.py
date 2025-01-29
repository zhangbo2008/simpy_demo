from functools import partial, wraps
import simpy
# 利用回调函数来监控变化.
def patch_resource(resource, pre=None, post=None):
    """Patch *resource* so that it calls the callable *pre* before each
    put/get/request/release operation and the callable *post* after each
    operation.  The only argument to these functions is the resource
    instance.

    """
    def get_wrapper(func):
        # Generate a wrapper for put/get/request/release
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is the actual wrapper
            # Call "pre" callback
            if pre:
                pre(resource)

            # Perform actual operation
            ret = func(*args, **kwargs)

            # Call "post" callback
            if post:
                post(resource)

            return ret
        return wrapper

    # Replace the original operations with our wrapper
    for name in ['put', 'get', 'request', 'release']:
        if hasattr(resource, name):
            setattr(resource, name, get_wrapper(getattr(resource, name)))

def monitor(data, resource):
    """This is our monitoring callback."""
    item = (
        resource._env.now,  # The current simulation time
        resource.count,  # The number of users
        len(resource.queue),  # The number of queued processes
    )
    data.append(item)

def test_process(env, res):
    with res.request() as req:
        yield req
        yield env.timeout(1)

env = simpy.Environment()

res = simpy.Resource(env, capacity=1)
data = []
# Bind *data* as first argument to monitor()
# see https://docs.python.org/3/library/functools.html#functools.partial
monitor = partial(monitor, data)
patch_resource(res, post=monitor)  # Patches (only) this resource instance

p = env.process(test_process(env, res))
env.run(p)

print(data)






















print('通过重写resource来实现监控, relearse里面加点东西即可.')
import simpy

class MonitoredResource(simpy.Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []

    def request(self, *args, **kwargs):
        self.data.append((self._env.now, len(self.queue)))
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.data.append((self._env.now, len(self.queue)))
        return super().release(*args, **kwargs)

def test_process(env, res):
    with res.request() as req:
        yield req
        yield env.timeout(1)

env = simpy.Environment()

res = MonitoredResource(env, capacity=1)
p1 = env.process(test_process(env, res))
p2 = env.process(test_process(env, res))
env.run()

print(res.data)







