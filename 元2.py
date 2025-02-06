# 改成4个车运5个货物.
def car(env, name, store, driving_time, charge_duration):
    # Simulate driving to the BCS
    yield env.timeout(driving_time)

    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    while 1:
        item = yield store.get()
        # Charge the battery
        print(f'%s 开始运输  货物{item} at %s ' % (name, env.now))

        yield env.timeout(charge_duration) # 运输用5秒来回.
        print('%s 回来了时间是 %s' % (name, env.now))
import simpy
env = simpy.Environment()
store =  simpy.Store(env, capacity=5)
for i  in range(5):
    store.put(i)

for i in range(4):
    env.process(car(env, 'Car %d' % i, store, i+1, 5))# 4个车, 分别1,2,3,4 秒进入.
env.run()
        
        
        
