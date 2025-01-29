# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html



import time
import simpy
env = simpy.Environment()
from simpy.util import start_delayed
from random import seed, randint
seed(23)

import simpy

class EV:  # 这里面2个事件, 一种叫passive主动触发, 一种是reactive被动
    def __init__(self, env):
        self.env = env
        #====19行和20行, 19行写上面那么就先打印开始开电池,再打印开始开车, 如果反过来, 那么就开始打印开车,然后打印开始开电池. 底层是env.process会让事件进行注册,注册顺序就是运行顺序, 这是异步框架, 所以只有一个进程其实.利用yield让出来cpu来模拟多进程.这种方法让进程之间的通讯变得非常简单可控.是目前最好的方案.
        self.bat_ctrl_proc = env.process(self.bat_ctrl(env))
        self.drive_proc = env.process(self.drive(env))
        self.bat_ctrl_reactivate = env.event() # 电池反应.  当汽车park时候,让他开始充电.所以电池是被动.汽车是主动来触发的.

    def drive(self, env):
        while True:
            # Drive for 20-40 min

            print('开始开车')
            yield env.timeout(randint(20, 40))

            # Park for 1–6 hours
            print('Start parking at', env.now)
            self.bat_ctrl_reactivate.succeed()  # "reactivate"
            self.bat_ctrl_reactivate = env.event()
            yield env.timeout(randint(60, 360))
            print('Stop parking at', env.now)

    def bat_ctrl(self, env):
        while True:
            print('开始开电池')
            print('Bat. ctrl. passivating at', env.now)
            yield self.bat_ctrl_reactivate  # "passivate"---这行走完
            print('Bat. ctrl. reactivated at', env.now)

            # Intelligent charging behavior here …
            yield env.timeout(randint(60, 90))

env = simpy.Environment()
ev = EV(env)
env.run(until=150)