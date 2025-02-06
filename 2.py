# Bank, 3 clerks.py
import salabim as sim


class CustomerGenerator(sim.Component):
    def process(self):
        while True:
            Customer()
            self.hold(sim.Uniform(5, 15).sample()) # 用来表示 每等一个随机事件, 就新创立一个客户对象.


class Customer(sim.Component):
    def process(self):
        self.enter(waitingline) # 客户上来就进入等待队列.
        for clerk in clerks:  # 然后看所有的服务员.
            if clerk.ispassive():  # 如果有一个服务员是非工作状态, 那么就激活这个服务员.
                clerk.activate() 
                break  # activate at most one clerk
        self.passivate()# 到这里就表示没有服务员可以被服务, 那么标记这个客户为迟钝状态. passive被动的. passive表示消极,被动.


class Clerk(sim.Component):
    def process(self):
        while True: # 服务员一直循环工作
            while len(waitingline) == 0:# 当客户等待队列是空的,那么服务员标记为被动的.
                self.passivate()
            self.customer = waitingline.pop() # 等待队列弹出一个.
            self.hold(30) # 服务30秒
            self.customer.activate() # 服务完再标记为活动的.活动时候不接受新任务.


env = sim.Environment(trace=False)
CustomerGenerator()
clerks = [Clerk() for _ in range(3)]

waitingline = sim.Queue("waitingline")

env.run(till=50000)
waitingline.print_histograms()

waitingline.print_info()