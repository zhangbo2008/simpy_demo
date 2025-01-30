# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html



import time
import simpy
env = simpy.Environment()
from simpy.util import start_delayed
from random import seed, randint
seed(23)

import simpy
class EV:
    def __init__(self, env):
        self.env = env
        self.drive_proc = env.process(self.drive(env))

    def drive(self, env):
        while True:
            # Drive for 20-40 min
            yield env.timeout(randint(20, 40))

            # Park for 1–6 hours
            print('Start parking at', env.now)
            charging = env.process(self.bat_ctrl(env))
            parking = env.timeout(randint(60, 360))
            yield charging & parking  # 出让cpu给这两个进程, 让他们都成功时候我们再要回cpu,充满了并且也停满了再开走. 如果两个只有一个成功, 那么等到2个都成功时候才要回cpu。这样才符合现实逻辑.
            print('Stop parking at', env.now)

    def bat_ctrl(self, env):
        print('Bat. ctrl. started at', env.now)
        # Intelligent charging behavior here …
        yield env.timeout(randint(30, 90))
        print('Bat. ctrl. done at', env.now)

env = simpy.Environment()
ev = EV(env)
env.run(until=310)