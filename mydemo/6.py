# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html




import simpy
env = simpy.Environment()
from simpy.util import start_delayed

def test_condition(env):
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 | t2
    assert ret == {t1: 'spam'}

    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 & t2
    assert ret == {t1: 'spam', t2: 'eggs'}

    # You can also concatenate & and |
    e1, e2, e3 = [env.timeout(i) for i in range(3)]
    yield (e1 | e2) & e3
    print(e1,e2,e3)
    print(list((e.processed for e in [e1, e2, e3])))
    print( all(e.processed for e in [e1, e2, e3]))

proc = env.process(test_condition(env))
env.run()



def fetch_values_of_multiple_events(env):
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    print(env.now)
    r1, r2 = (yield t1 & t2).values()
    assert r1 == 'spam' and r2 == 'eggs'
    print(r1,r2,env.now)
    return  r1,r2

proc = env.process(fetch_values_of_multiple_events(env))
print(proc)
env.run()














