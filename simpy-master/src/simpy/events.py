"""
This module contains the basic event types used in SimPy.

The base class for all events is :class:`Event`. Though it can be directly
used, there are several specialized subclasses of it.
这是所有的事件的类别一共有5个.
.. autosummary::

    ~simpy.events.Event
    ~simpy.events.Timeout
    ~simpy.events.Process
    ~simpy.events.AnyOf
    ~simpy.events.AllOf

"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    NewType,
    Optional,
    Tuple,
    TypeVar,
)

from simpy.exceptions import Interrupt

if TYPE_CHECKING:
    from types import FrameType

    from simpy.core import Environment, SimTime

PENDING: object = object()
"""Unique object to identify pending values of events."""

EventPriority = NewType('EventPriority', int)

URGENT: EventPriority = EventPriority(0)
"""Priority of interrupts and process initialization events."""
NORMAL: EventPriority = EventPriority(1)
"""Default priority used by events."""


class Event:
    """An event that may happen at some point in time.

    An event

    - may happen (:attr:`triggered` is ``False``),
    - is going to happen (:attr:`triggered` is ``True``) or
    - has happened (:attr:`processed` is ``True``).

    Every event is bound to an environment *env* and is initially not
    triggered. Events are scheduled for processing by the environment after
    they are triggered by either :meth:`succeed`, :meth:`fail` or
    :meth:`trigger`. These methods also set the *ok* flag and the *value* of
    the event.每一个事件被三个方法触发succeed, fail, trigger

    An event has a list of :attr:`callbacks`. A callback can be any callable.
    Once an event gets processed, all callbacks will be invoked with the event
    as the single argument. Callbacks can check if the event was successful by
    examining *ok* and do further processing with the *value* it has produced.
    事件都有一个callbacks列表
    
    

    Failed events are never silently ignored and will raise an exception upon
    being processed. If a callback handles an exception, it must set
    :attr:`defused` to ``True`` to prevent this.失败的event会引发一个异常,如果回调处理异常,那么他必须设置defused为true来避免异常.

    This class also implements ``__and__()`` (``&``) and ``__or__()`` (``|``).
    If you concatenate two events using one of these operators,
    a :class:`Condition` event is generated that lets you wait for both or one
    of them.

    """

    _ok: bool
    _defused: bool
    _value: Any = PENDING #表示value可以是任意对象.

    def __init__(self, env: Environment):
        self.env = env
        """The :class:`~simpy.core.Environment` the event lives in."""
        self.callbacks: EventCallbacks = []
        """List of functions that are called when the event is processed."""

    def __repr__(self) -> str:
        """Return the description of the event (see :meth:`_desc`) with the id
        of the event."""
        return f'<{self._desc()} object at {id(self):#x}>'

    def _desc(self) -> str:
        """Return a string *Event()*."""
        return f'{self.__class__.__name__}()'

    @property
    def triggered(self) -> bool:
        """Becomes ``True`` if the event has been triggered and its callbacks
        are about to be invoked."""
        return self._value is not PENDING

    @property
    def processed(self) -> bool:
        """Becomes ``True`` if the event has been processed (e.g., its
        callbacks have been invoked)."""
        return self.callbacks is None

    @property
    def ok(self) -> bool:
        """Becomes ``True`` when the event has been triggered successfully.

        A "successful" event is one triggered with :meth:`succeed()`.

        :raises AttributeError: if accessed before the event is triggered.

        """
        return self._ok

    @property
    def defused(self) -> bool:
        """Becomes ``True`` when the failed event's exception is "defused".

        When an event fails (i.e. with :meth:`fail()`), the failed event's
        `value` is an exception that will be re-raised when the
        :class:`~simpy.core.Environment` processes the event (i.e. in
        :meth:`~simpy.core.Environment.step()`).

        It is also possible for the failed event's exception to be defused by
        setting :attr:`defused` to ``True`` from an event callback. Doing so
        prevents the event's exception from being re-raised when the event is
        processed by the :class:`~simpy.core.Environment`.

        """
        return hasattr(self, '_defused')

    @defused.setter
    def defused(self, value: bool) -> None:
        self._defused = True

    @property
    def value(self) -> Optional[Any]:
        """The value of the event if it is available.

        The value is available when the event has been triggered.

        Raises :exc:`AttributeError` if the value is not yet available.

        """
        if self._value is PENDING:
            raise AttributeError(f'Value of {self} is not yet available')
        return self._value

    def trigger(self, event: Event) -> None:
        """Trigger the event with the state and value of the provided *event*.
        Return *self* (this event instance).

        This method can be used directly as a callback function to trigger
        chain reactions.

        """
        self._ok = event._ok
        self._value = event._value
        self.env.schedule(self)

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
        return self

    def fail(self, exception: Exception) -> Event:
        """Set *exception* as the events value, mark it as failed and schedule
        it for processing by the environment. Returns the event instance.

        Raises :exc:`TypeError` if *exception* is not an :exc:`Exception`.

        Raises :exc:`RuntimeError` if this event has already been triggered.

        """
        if self._value is not PENDING:
            raise RuntimeError(f'{self} has already been triggered')
        if not isinstance(exception, BaseException):
            raise TypeError(f'{exception} is not an exception.')
        self._ok = False
        self._value = exception
        self.env.schedule(self)
        return self

    def __and__(self, other: Event) -> Condition:
        """Return a :class:`~simpy.events.Condition` that will be triggered if
        both, this event and *other*, have been processed."""
        return Condition(self.env, Condition.all_events, [self, other])

    def __or__(self, other: Event) -> Condition:
        """Return a :class:`~simpy.events.Condition` that will be triggered if
        either this event or *other* have been processed (or even both, if they
        happened concurrently)."""
        return Condition(self.env, Condition.any_events, [self, other])


EventType = TypeVar('EventType', bound=Event)
EventCallback = Callable[[EventType], None]
EventCallbacks = List[EventCallback]

# timeout事件
class Timeout(Event):
    """A :class:`~simpy.events.Event` that gets processed after a *delay* has
    passed.

    This event is automatically triggered when it is created.


    """

    def __init__(
        self,
        env: Environment,
        delay: SimTime,
        value: Optional[Any] = None,
    ):
        if delay < 0:
            raise ValueError(f'Negative delay {delay}')
        # NOTE: The following initialization code is inlined from
        # Event.__init__() for performance reasons.
        self.env = env
        self.callbacks: EventCallbacks = []
        self._value = value
        self._delay = delay
        self._ok = True
        env.schedule(self, NORMAL, delay) # 优先级普通, delay是时间.

    def _desc(self) -> str:
        """Return a string *Timeout(delay[, value=value])*."""
        value_str = '' if self._value is None else f', value={self.value}'
        return f'{self.__class__.__name__}({self._delay}{value_str})'

# 初始化一个进程, 被类Process自动调用.
class Initialize(Event):
    """Initializes a process. Only used internally by :class:`Process`.

    This event is automatically triggered when it is created.

    """

    def __init__(self, env: Environment, process: Process):
        # NOTE: The following initialization code is inlined from
        # Event.__init__() for performance reasons.
        self.env = env
        self.callbacks: EventCallbacks = [process._resume]# 这里回调是resume函数.
        self._value: Any = None

        # The initialization events needs to be scheduled as urgent so that it
        # will be handled before interrupts. Otherwise, a process whose
        # generator has not yet been started could be interrupted.
        self._ok = True
        env.schedule(self, URGENT)#初始化要设置为最高优先级,因为如果有其他事件要中断这个event, 那么需要这个event初始化, 才能做catch这个interupt事件. 所以初始化要一开始都做好,才能正确处理进程间通讯.


class Interruption(Event):
    """Immediately schedules an :class:`~simpy.exceptions.Interrupt` exception
    with the given *cause* to be thrown into *process*.

    This event is automatically triggered when it is created.# 这里说立即触发从301行能看出来.

    """ # casuse这个原因引发, 然后中断进程process的这个事件我们叫interrption.

    def __init__(self, process: Process, cause: Optional[Any]):
        # NOTE: The following initialization code is inlined from
        # Event.__init__() for performance reasons.
        self.env = process.env # process是即将被中断的进程.
        self.callbacks: EventCallbacks = [self._interrupt] #设置这个事件的回调, 也就是真正的处理.
        self._value = Interrupt(cause)
        self._ok = False
        self._defused = True

        if process._value is not PENDING:
            raise RuntimeError(f'{process} has terminated and cannot be interrupted.')

        if process is self.env.active_process:
            raise RuntimeError('A process is not allowed to interrupt itself.')

        self.process = process
        self.env.schedule(self, URGENT) #注意这些schedule没写delay_time,默认参数就是0,表示立即触发.

    def _interrupt(self, event: Event) -> None:
        # Ignore dead processes. Multiple concurrently scheduled interrupts
        # cause this situation. If the process dies while handling the first
        # one, the remaining interrupts must be ignored.
        if self.process._value is not PENDING: # 只有value是pending的才是还没做完的事件.做过的事件没必要中断了.
            return

        # A process never expects an interrupt and is always waiting for a
        # target event. Remove the process from the callbacks of the target.
        self.process._target.callbacks.remove(self.process._resume)

        self.process._resume(self)


ProcessGenerator = Generator[Event, Any, Any]

# 最重要的process事件.使用携程来实现,他可以利用yield来暂停和resume
class Process(Event):
    """Process an event yielding generator.

    A generator (also known as a coroutine) can suspend its execution by
    yielding an event. ``Process`` will take care of resuming the generator
    with the value of that event once it has happened. The exception of failed
    events is thrown into the generator.

    ``Process`` itself is an event, too. It is triggered, once the generator
    returns or raises an exception. The value of the process is the return
    value of the generator or the exception, respectively.

    Processes can be interrupted during their execution by :meth:`interrupt`.

    """

    def __init__(self, env: Environment, generator: ProcessGenerator):
        if not hasattr(generator, 'throw'):
            # Implementation note: Python implementations differ in the
            # generator types they provide. Cython adds its own generator type
            # in addition to the CPython type, which renders a type check
            # impractical. To work around this issue, we check for attribute
            # name instead of type and optimistically assume that all objects
            # with a ``throw`` attribute are generators.
            # Remove this workaround if it causes issues in production! # 生产环境如果报错就删了这行代码if
            raise ValueError(f'{generator} is not a generator.')

        # NOTE: The following initialization code is inlined from
        # Event.__init__() for performance reasons.
        self.env = env
        self.callbacks: EventCallbacks = []

        self._generator = generator

        # Schedule the start of the execution of the process.
        self._target: Event = Initialize(env, self)

    def _desc(self) -> str:
        """Return a string *Process(process_func_name)*."""
        return f'{self.__class__.__name__}({self.name})'

    @property
    def target(self) -> Event:
        """The event that the process is currently waiting for.

        Returns ``None`` if the process is dead, or it is currently being
        interrupted.

        """
        return self._target

    @property
    def name(self) -> str:
        """Name of the function used to start the process."""
        return self._generator.__name__  # type: ignore

    @property
    def is_alive(self) -> bool:
        """``True`` until the process generator exits."""
        return self._value is PENDING

    def interrupt(self, cause: Optional[Any] = None) -> None: #把自己停止.
        """Interrupt this process optionally providing a *cause*.

        A process cannot be interrupted if it already terminated. A process can
        also not interrupt itself. Raise a :exc:`RuntimeError` in these
        cases.

        """
        Interruption(self, cause)

    def _resume(self, event: Event) -> None:# 让进程真正开始执行的函数,也就是执行函数.这里叫resume为了架构统一.设计成恢复执行和执行是一个函数.
        """Resumes the execution of the process with the value of *event*. If
        the process generator exits, the process itself will get triggered with
        the return value or the exception of the generator."""
        # Mark the current process as active.
        self.env._active_proc = self # 首先定义环境正在运行的进程是自己.

        while True:
            # Get next event from process
            try:
                if event._ok:
                    event = self._generator.send(event._value)
                else:
                    # The process has no choice but to handle the failed event
                    # (or fail itself).
                    event._defused = True

                    # Create an exclusive copy of the exception for this
                    # process to prevent traceback modifications by other
                    # processes.
                    exc = type(event._value)(*event._value.args)
                    exc.__cause__ = event._value
                    event = self._generator.throw(exc)
            except StopIteration as e:
                # Process has terminated.
                event = None  # type: ignore
                self._ok = True
                self._value = e.args[0] if len(e.args) else None
                self.env.schedule(self)
                break
            except BaseException as e:
                # Process has failed.
                event = None  # type: ignore
                self._ok = False
                # Strip the frame of this function from the traceback as it
                # does not add any useful information.
                e.__traceback__ = e.__traceback__.tb_next  # type: ignore
                self._value = e
                self.env.schedule(self)
                break

            # Process returned another event to wait upon.
            try:
                # Be optimistic and blindly access the callbacks attribute.
                if event.callbacks is not None:
                    # The event has not yet been triggered. Register callback
                    # to resume the process if that happens.
                    event.callbacks.append(self._resume)
                    break
            except AttributeError:
                # Our optimism didn't work out, figure out what went wrong and
                # inform the user.
                if hasattr(event, 'callbacks'):
                    raise

                msg = f'Invalid yield value "{event}"'
                descr = _describe_frame(self._generator.gi_frame)
                raise RuntimeError(f'\n{descr}{msg}') from None

        self._target = event
        self.env._active_proc = None


class ConditionValue: # 作为condition时间的返回值.
    """Result of a :class:`~simpy.events.Condition`. It supports convenient
    dict-like access to the triggered events and their values. The events are
    ordered by their occurrences in the condition."""

    def __init__(self) -> None:
        self.events: List[Event] = []

    def __getitem__(self, key: Event) -> Any:
        if key not in self.events:
            raise KeyError(str(key))

        return key._value

    def __contains__(self, key: Event) -> bool:
        return key in self.events

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConditionValue):
            return self.events == other.events
        elif isinstance(other, dict):
            return self.todict() == other
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f'<ConditionValue {self.todict()}>'

    def __iter__(self) -> Iterator[Event]:
        return self.keys()

    def keys(self) -> Iterator[Event]:
        return (event for event in self.events)

    def values(self) -> Iterator[Any]:
        return (event._value for event in self.events)

    def items(self) -> Iterator[Tuple[Event, Any]]:
        return ((event, event._value) for event in self.events)

    def todict(self) -> Dict[Event, Any]:
        return {event: event._value for event in self.events}


class Condition(Event):
    """An event that gets triggered once the condition function *evaluate*
    returns ``True`` on the given list of *events*.

    The value of the condition event is an instance of :class:`ConditionValue`
    which allows convenient access to the input events and their values. The
    :class:`ConditionValue` will only contain entries for those events that
    occurred before the condition is processed.

    If one of the events fails, the condition also fails and forwards the
    exception of the failing event.

    The *evaluate* function receives the list of target events and the number
    of processed events in this list: ``evaluate(events, processed_count)``. If
    it returns ``True``, the condition is triggered. The
    :func:`Condition.all_events()` and :func:`Condition.any_events()` functions
    are used to implement *and* (``&``) and *or* (``|``) for events.

    Condition events can be nested.

    """

    def __init__(
        self,
        env: Environment,
        evaluate: Callable[[Tuple[Event, ...], int], bool],
        events: Iterable[Event],
    ):
        super().__init__(env)
        self._evaluate = evaluate
        self._events = tuple(events)
        self._count = 0

        if not self._events:
            # Immediately succeed if no events are provided.
            self.succeed(ConditionValue())
            return

        # Check if events belong to the same environment.
        for event in self._events:
            if self.env != event.env:
                raise ValueError(
                    'It is not allowed to mix events from different environments'
                )

        # Check if the condition is met for each processed event. Attach
        # _check() as a callback otherwise.
        for event in self._events:
            if event.callbacks is None:
                self._check(event)
            else:
                event.callbacks.append(self._check)

        # Register a callback which will build the value of this condition
        # after it has been triggered.
        assert isinstance(self.callbacks, list)
        self.callbacks.append(self._build_value)

    def _desc(self) -> str:
        """Return a string *Condition(evaluate, [events])*."""
        return f'{self.__class__.__name__}({self._evaluate.__name__}, {self._events})'

    def _populate_value(self, value: ConditionValue) -> None:
        """Populate the *value* by recursively visiting all nested
        conditions."""

        for event in self._events:
            if isinstance(event, Condition):
                event._populate_value(value)
            elif event.callbacks is None:
                value.events.append(event)

    def _build_value(self, event: Event) -> None:
        """Build the value of this condition."""
        self._remove_check_callbacks()
        if event._ok:
            self._value = ConditionValue()
            self._populate_value(self._value)

    def _remove_check_callbacks(self) -> None:
        """Remove _check() callbacks from events recursively.

        Once the condition has triggered, the condition's events no longer need
        to have _check() callbacks. Removing the _check() callbacks is
        important to break circular references between the condition and
        untriggered events.

        """
        for event in self._events:
            if event.callbacks and self._check in event.callbacks:
                event.callbacks.remove(self._check)
            if isinstance(event, Condition):
                event._remove_check_callbacks()

    def _check(self, event: Event) -> None:
        """Check if the condition was already met and schedule the *event* if
        so."""
        if self._value is not PENDING:
            return

        self._count += 1

        if not event._ok:
            # Abort if the event has failed.
            event._defused = True
            self.fail(event._value)
        elif self._evaluate(self._events, self._count):
            # The condition has been met. The _build_value() callback will
            # populate the ConditionValue once this condition is processed.
            self.succeed()

    @staticmethod
    def all_events(events: Tuple[Event, ...], count: int) -> bool:
        """An evaluation function that returns ``True`` if all *events* have
        been triggered.""" #count是触发的数量.
        return len(events) == count

    @staticmethod
    def any_events(events: Tuple[Event, ...], count: int) -> bool:
        """An evaluation function that returns ``True`` if at least one of
        *events* has been triggered."""
        return count > 0 or len(events) == 0


class AllOf(Condition):
    """A :class:`~simpy.events.Condition` event that is triggered if all of
    a list of *events* have been successfully triggered. Fails immediately if
    any of *events* failed.

    """

    def __init__(self, env: Environment, events: Iterable[Event]):
        super().__init__(env, Condition.all_events, events)


class AnyOf(Condition):
    """A :class:`~simpy.events.Condition` event that is triggered if any of
    a list of *events* has been successfully triggered. Fails immediately if
    any of *events* failed.

    """

    def __init__(self, env: Environment, events: Iterable[Event]):
        super().__init__(env, Condition.any_events, events)


def _describe_frame(frame: FrameType) -> str:
    """Print filename, line number and function name of a stack frame."""
    filename, name = frame.f_code.co_filename, frame.f_code.co_name
    lineno = frame.f_lineno

    with open(filename) as f:
        for no, line in enumerate(f):
            if no + 1 == lineno:
                return (
                    f'  File "{filename}", line {lineno}, in {name}\n'
                    f'    {line.strip()}\n'
                )
        return f'  File "{filename}", line {lineno}, in {name}\n'
