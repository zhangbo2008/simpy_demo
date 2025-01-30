import simpy
from collections import namedtuple

Machine = namedtuple('Machine', 'size, duration')
m1 = Machine(1, 2)  # Small and slow  # 让货物有2个属性,一个size, 一个duration 是上货速度.
m2 = Machine(2, 1)  # Big and fast

env = simpy.Environment()
machine_shop = simpy.FilterStore(env, capacity=2) # 一个机器最多2个人操作.这里面用户又取东西, 又放东西.
machine_shop.items = [m1, m2]  # Pre-populate the machine shop

def user(name, env, ms, size):
    print(f'{name}来了')
    machine = yield ms.get(lambda machine: machine.size == size)
    print(name, 'got', machine, 'at', env.now)
    yield env.timeout(machine.duration)
    yield ms.put(machine)
    print(name, 'released', machine, 'at', env.now)


users = [env.process(user(i, env, machine_shop, (i % 2) + 1))
         for i in range(3)]
env.run()