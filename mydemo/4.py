# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html




import simpy
env = simpy.Environment()
def sub(env): # 子进程
    yield env.timeout(1)
    return 23

def parent(env): #父进程
    ret = yield env.process(sub(env))
    return ret

a=env.run(env.process(parent(env)))
print(a)


















