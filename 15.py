import simpy
class GasStation:
    def __init__(self, env):
        self.fuel_dispensers = simpy.Resource(env, capacity=2)
        self.gas_tank = simpy.Container(env, init=100, capacity=1000)
        self.mon_proc = env.process(self.monitor_tank(env))

    def monitor_tank(self, env):
        print('开始监控石油的存量')
        while True:
            if self.gas_tank.level < 100:
                print(f'Calling tanker at {env.now}')
                env.process(tanker(env, self))
            yield env.timeout(15)


def tanker(env, gas_station):
    yield env.timeout(10)  # Need 10 Minutes to arrive
    print(f'Tanker arriving at {env.now}')
    amount = gas_station.gas_tank.capacity - gas_station.gas_tank.level
    yield gas_station.gas_tank.put(amount)


def car(name, env, gas_station):
    print(f'Car {name} arriving at {env.now}')
    with gas_station.fuel_dispensers.request() as req:
        yield req
        print(f'Car {name} starts refueling at {env.now}')
        yield gas_station.gas_tank.get(40) #每次消耗40汽油.
        yield env.timeout(5)
        print(f'Car {name} done refueling at {env.now}')


def car_generator(env, gas_station):
    for i in range(4):
        env.process(car(i, env, gas_station))
        yield env.timeout(5)


env = simpy.Environment()
gas_station = GasStation(env)
env.process(car_generator(env, gas_station))
env.run(35) # env.run方法调用后, 会找env.process注册过的事件, 然后按照这个事件注册的顺序来进行运行. 这个代码里面注册 第六行, 然后再注册的 是第42行.