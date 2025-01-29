# 24以后的都是demo研究一下.
'''
This example models a bank counter and customers arriving at random times. Each customer has a certain patience. She waits to get to the counter until she’s at the end of her tether. If she gets to the counter, she uses it for a while before releasing it.

New customers are created by the source process every few time steps.
'''


"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

"""

import random

import simpy

RANDOM_SEED = 42
NEW_CUSTOMERS = 5  # Total number of customers
INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience


def source(env, number, interval, counter):
    """Source generates customers randomly"""
    for i in range(number):
        c = customer(env, f'Customer{i:02d}', counter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)   # https://blog.csdn.net/m0_52733659/article/details/123682527  这里使用泊松分布来推导指数分布. 泊松分布是从二项分布推导的. 这里是这个python源码逆采样的推导: https://www.cnblogs.com/zhangbo2008/p/18694562
        yield env.timeout(t)


def customer(env, name, counter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print(f'{arrive:7.4f} {name}: Here I am')

    with counter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the counter or abort at the end of our tether
        results = yield req | env.timeout(patience) # 等待服务或者失去耐心.

        wait = env.now - arrive

        if req in results:
            # We got to the counter
            print(f'{env.now:7.4f} {name}: Waited {wait:6.3f}')

            tib = random.expovariate(1.0 / time_in_bank) # time_in_bank 表示柜员一次服务客户,平均12秒.
            yield env.timeout(tib)
            print(f'{env.now:7.4f} {name}: Finished')

        else:
            # We reneged
            print(f'{env.now:7.4f} {name}: RENEGED after {wait:6.3f}')


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=1) # counter是销售员, 这里面只有一个.
env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))
env.run()



