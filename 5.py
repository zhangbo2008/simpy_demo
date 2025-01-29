# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html




import simpy
env = simpy.Environment()
from simpy.util import start_delayed

def sub(env):
    yield env.timeout(1)
    return 23

def parent(env):
    sub_proc = yield start_delayed(env, sub(env), delay=3)
    ret = yield sub_proc
    return ret

a=env.run(env.process(parent(env)))
print(a)


















