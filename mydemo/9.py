# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html



import time
import simpy
env = simpy.Environment()
from simpy.util import start_delayed
from random import seed, randint
seed(23)
class EV:
    def __init__(self, env):
        self.env = env
        self.drive_proc = env.process(self.drive(env))

    def drive(self, env):
        while True:
            # Drive for 20-40 min
            yield env.timeout(randint(20, 40))

            # Park for 1 hour
            print('Start parking at', env.now)
            charging = env.process(self.bat_ctrl(env))
            parking = env.timeout(60)
            yield charging | parking
            if not charging.triggered: #如果触发的是停车到时了,并且充电没充满,那么我们就给充电进程一个中断, 然后开走.
                # Interrupt charging if not already done.
                charging.interrupt('Need to go!')
            print('Stop parking at', env.now)

    def bat_ctrl(self, env):
        print('Bat. ctrl. started at', env.now)
        try:
            yield env.timeout(randint(60, 90))  # 正常充电,
            print('Bat. ctrl. done at', env.now)
        except simpy.Interrupt as i:  # 其他进程触发了中断,那么走这里.
            # Onoes! Got interrupted before the charging was done.
            print('Bat. ctrl. interrupted at', env.now, 'msg:',
                  i.cause)

env = simpy.Environment()
ev = EV(env)
env.run(until=100)