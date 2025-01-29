import simpy
import time
import simpy.rt

def slow_proc(env):
   while 1:
    time.sleep(0.2)  # Heavy computation :-)
    print('running',env.now)
    yield env.timeout(1)

env = simpy.rt.RealtimeEnvironment(factor=0.2)
proc = env.process(slow_proc(env))
try:
    env.run(until=proc)
    print('Everything alright')
except RuntimeError:
    print('Simulation is too slow')