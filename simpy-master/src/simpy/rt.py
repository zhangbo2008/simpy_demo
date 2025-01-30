"""Execution environment for events that synchronizes passing of time
with the real-time (aka *wall-clock time*).

"""

from time import monotonic, sleep

from simpy.core import EmptySchedule, Environment, Infinity, SimTime


class RealtimeEnvironment(Environment):
    """Execution environment for an event-based simulation which is
    synchronized with the real-time (also known as wall-clock time). A time
    step will take *factor* seconds of real time (one second by default).
    A step from ``0`` to ``3`` with a ``factor=0.5`` will, for example, take at
    least
    1.5 seconds.

    The :meth:`step()` method will raise a :exc:`RuntimeError` if a time step
    took too long to compute. This behaviour can be disabled by setting
    *strict* to ``False``.

    """

    def __init__(
        self,
        initial_time: SimTime = 0,
        factor: float = 1.0,
        strict: bool = True,
    ):
        Environment.__init__(self, initial_time)

        self.env_start = initial_time
        self.real_start = monotonic() # 现实时间, 叫单调时间. 应该是当前计算机启动的时间,毫秒级. 可以用来做计算时间差.
        self._factor = factor
        self._strict = strict

    @property
    def factor(self) -> float:
        """Scaling factor of the real-time."""
        return self._factor

    @property
    def strict(self) -> bool:
        """Running mode of the environment. :meth:`step()` will raise a
        :exc:`RuntimeError` if this is set to ``True`` and the processing of
        events takes too long."""
        return self._strict

    def sync(self) -> None:
        """Synchronize the internal time with the current wall-clock time.

        This can be useful to prevent :meth:`step()` from raising an error if
        a lot of time passes between creating the RealtimeEnvironment and
        calling :meth:`run()` or :meth:`step()`.

        """
        self.real_start = monotonic()

    def step(self) -> None:
        """Process the next event after enough real-time has passed for the
        event to happen.

        The delay is scaled according to the real-time :attr:`factor`. With
        :attr:`strict` mode enabled, a :exc:`RuntimeError` will be raised, if
        the event is processed too slowly.

        """
        evt_time = self.peek() #看一下下一个事件发生的时间.是模拟事件.

        if evt_time is Infinity:
            raise EmptySchedule
# self.factor是模拟事件每一步对应现实事件多少秒.
        real_time = self.real_start + (evt_time - self.env_start) * self.factor # 换算成现实时间下一个事件发送的时间.

        if self.strict and monotonic() - real_time > self.factor: # 严格值的是,如果step里面的时间大于了模拟时间的单个步长.这个需要mydemo/19.py 这个代码来理解.
            
            '''
            经过19.py 测试,factor你越大越没事,env次数越少. factor表示现实世界两次step时间间隔.
            而实际上代码里面的时间间隔还有一个时间间隔, 这个跟电脑有关也跟代码写的有关, 比如19.py里面写的是0.2秒睡眠.
            所以我们测试发现factor如果写0.1秒那么这里代码76行. monotonic() - real_time=0.2, facotr是0.1. 显然现实中的流速比模拟step的流速要快了.这种是没办法让代码能很好模拟现实中的效果的.
            而我们写factor=5.
            那么 左边还是0.2, 右边是5. 显然不会走76行逻辑.这是可以的, 因为现实中走0.2秒,但是我们模拟假设他走5秒.我们还是装作慢动作.这在我们这个模拟逻辑中是可以的.等于我们把现实中的时间轴给慢放了. 但是模拟一般不允许快放. 当然你如果想快放可以把strict=False即可.这些都跟你业务逻辑有关.
            
            
            '''
            
            # Events scheduled for time *t* may take just up to *t+1*
            # for their computation, before an error is raised.
            delta = monotonic() - real_time
            raise RuntimeError(f'Simulation too slow for real time ({delta:.3f}s).')
                # 最后上面的句子也说了, 模拟太慢, 而现实中太快. 这种是一般意义来说不希望看到的.
        # Sleep in a loop to fix inaccuracies of windows (see
        # http://stackoverflow.com/a/15967564 for details) and to ignore
        # interrupts.
        while True: # 最后就是矫正我们把现实中代码走的时间,减去monotonic(). 举例子也就是 上面的 4.8秒.让后我们sleep 4.8即可.这样就校准了模拟事件跟真实时间. 这里面如果delta<=0,我们当然就直接break走掉.因为时间已经走了,再sleep也没用了.
            delta = real_time - monotonic()
            if delta <= 0:
                break
            sleep(delta)

        Environment.step(self)
