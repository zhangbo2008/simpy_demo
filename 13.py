import simpy

#=模拟3个任务互相抢. 设置一个任务完成与否的flag即可.无论如何这三个任务因为第三个任务的优先级高, 所以最终都需要用11秒来完成.
def resource_user(name, env, resource, wait, prio):
    yield env.timeout(wait)
    not_done=1
    while not_done:#没有做完任务就循环请求.
     with resource.request(priority=prio) as req:
        print(f'{name} requesting at {env.now} with priority={prio}')
        yield req
        print(f'{name} got resource at {env.now}')
        try:
            yield env.timeout(3) # 第一个进程尝试等三秒.第二个进程没更高优先级所以在8行卡主,拿不到资源, 第三个进程优先级高,所以他运行到第8行来触发抢资源.他一抢, 第一个进程就走12行,进行被抢的逻辑.
            not_done=0
        except simpy.Interrupt as interrupt:
            by = interrupt.cause.by
            usage = env.now - interrupt.cause.usage_since
            print(f'{name} got preempted by {by} at {env.now}'
                  f' after {usage}')
            print(f'{name}被抢了,重新等资源')
    print(f'{name}释放资源 at {env.now}')

env = simpy.Environment()
res = simpy.PreemptiveResource(env, capacity=1) # 这是一个可以被抢占的资源.
p1 = env.process(resource_user(1, env, res, wait=0, prio=0))
p2 = env.process(resource_user(2, env, res, wait=1, prio=0))
p3 = env.process(resource_user(3, env, res, wait=2, prio=-2))
env.run()