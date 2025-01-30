# simpy官网地址:
# https://simpy.readthedocs.io/en/latest/index.html






class School:
    def __init__(self, env):
        self.env = env
        self.class_ends = env.event()
        self.pupil_procs = [env.process(self.pupil()) for i in range(5)]  # 5个小孩上课, 打印之后, 27行停止等class_ends事件. 当19行succeed了, end事件就触发了, 这个样5个小孩继续循环了.
        self.bell_proc = env.process(self.bell())

    def bell(self):
        for i in range(2):
            yield self.env.timeout(45)
            self.class_ends.succeed()
            # print('继续让学生上课')
            self.class_ends = self.env.event()
            print('--------',env.now)

    def pupil(self):
        for i in range(2):
            print(r' \o/',env.now, end='')
            yield self.class_ends
import simpy
env = simpy.Environment()
school = School(env)
env.run()


















