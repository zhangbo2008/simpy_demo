import simpy




def resource_user(name, env, resource, wait, prio):
    yield env.timeout(wait)
    with resource.request(priority=prio) as req:
        print(f'{name} requesting at {env.now} with priority={prio}')
        yield req  # yield 是让出cpu意思, req表示等待req时候再拿回cpu
        print(f'{name} got resource at {env.now}')
        yield env.timeout(3) #等待3秒之后再拿回cpu执行后续代码, with块里面所以后续代码就是释放这个req.

env = simpy.Environment()
res = simpy.PriorityResource(env, capacity=1)
p1 = env.process(resource_user(1, env, res, wait=0, prio=0))
p2 = env.process(resource_user(2, env, res, wait=1, prio=0))
p3 = env.process(resource_user(3, env, res, wait=2, prio=-1))
env.run()