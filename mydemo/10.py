import simpy

def resource_user(env, resource):
    request = resource.request()  # Generate a request event
    yield request                 # Wait for access
    print('running',env.now)
    yield env.timeout(1)          # Do something

    resource.release(request)     # Release the resource
    print(env.now)

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
user = env.process(resource_user(env, res))
env.run()




def resource_user(env, resource):
    with resource.request() as req:  # Generate a request event
        yield req                    # Wait for access
        yield env.timeout(1)         # Do something
                                     # Resource released automatically
user = env.process(resource_user(env, res))
env.run()










res = simpy.Resource(env, capacity=1)

def print_stats(res):
    print(f'{res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')


def user(res):
    print_stats(res)
    with res.request() as req:
        yield req
        print_stats(res)
    print_stats(res)

procs = [env.process(user(res)), env.process(user(res))] #==同时启动2个user来消耗这个共享的资源.
env.run()  # 能看出来每一次申请, 都会进行当前状态的打印.
