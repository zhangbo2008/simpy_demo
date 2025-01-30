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
            self.class_ends.succeed() # 就是让这个事件成功继续运行. 源码
            '''
    def succeed(self, value: Optional[Any] = None) -> Event:
        """Set the event's value, mark it as successful and schedule it for
        processing by the environment. Returns the event instance.

        Raises :exc:`RuntimeError` if this event has already been triggered.

        """
        if self._value is not PENDING:
            raise RuntimeError(f'{self} has already been triggered')

        self._ok = True
        self._value = value
        self.env.schedule(self)
        return self    也就是设置ok, 和这次event的返回值, 然后调用schedule让env执行后续代码.
            '''
            # print('继续让学生上课')
            self.class_ends = self.env.event()
            print('--------',env.now)

    def pupil(self):
        for i in range(2):
            print(r' \o/',env.now, end='')
            yield self.class_ends #==这里就是等self.class_ends这个事件结束, 再进行继续print.
import simpy
env = simpy.Environment()
school = School(env)
env.run()


















