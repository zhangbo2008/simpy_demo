"""
Tests for forwarding exceptions from child to parent processes.

"""

import platform
import re
import textwrap
import traceback

import pytest


def test_error_forwarding(env):
    """Exceptions are forwarded from child to parent processes if there
    are any.

    """

    def child(env):
        raise ValueError('Onoes!')
        yield env.timeout(1)

    def parent(env):
        with pytest.raises(ValueError, match='Onoes!'):
            yield env.process(child(env))

    env.process(parent(env))
    env.run()


def test_no_parent_process(env):
    """Exceptions should be normally raised if there are no processes waiting
    for the one that raises something.

    """

    def child(env):
        raise ValueError('Onoes!')
        yield env.timeout(1)

    def parent(env):
        try:
            env.process(child(env))
            yield env.timeout(1)
        except Exception as err:
            pytest.fail(f'There should be no error ({err}).')

    env.process(parent(env))
    with pytest.raises(ValueError, match='Onoes!'):
        env.run()


def test_crashing_child_traceback(env):
    def panic(env):
        yield env.timeout(1)
        raise RuntimeError('Oh noes, roflcopter incoming... BOOM!')

    def root(env):
        try:
            yield env.process(panic(env))
            pytest.fail("Hey, where's the roflcopter?")
        except RuntimeError:
            # The current frame must be visible in the stacktrace.
            stacktrace = traceback.format_exc()
            assert 'yield env.process(panic(env))' in stacktrace
            assert "raise RuntimeError('Oh noes," in stacktrace

    env.process(root(env))
    env.run()


def test_exception_chaining(env):
    """Unhandled exceptions pass through the entire event stack. This must be
    visible in the stacktrace of the exception.

    """

    def child(env):
        yield env.timeout(1)
        raise RuntimeError('foo')

    def parent(env):
        child_proc = env.process(child(env))
        yield child_proc

    def grandparent(env):
        parent_proc = env.process(parent(env))
        yield parent_proc

    env.process(grandparent(env))
    try:
        env.run()
        pytest.fail('There should have been an exception')
    except RuntimeError:
        trace = traceback.format_exc()

        expected = (
            re.escape(
                textwrap.dedent(
                    """\
        Traceback (most recent call last):
          File "{path}tests/test_exceptions.py", line {line}, in child
            raise RuntimeError('foo')
        RuntimeError: foo

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "{path}tests/test_exceptions.py", line {line}, in parent
            yield child_proc
        RuntimeError: foo

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "{path}tests/test_exceptions.py", line {line}, in grandparent
            yield parent_proc
        RuntimeError: foo

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "{path}tests/test_exceptions.py", line {line}, in test_exception_chaining
            env.run()
          File "{path}simpy/core.py", line {line}, in run
            self.step()
          File "{path}simpy/core.py", line {line}, in step
            raise exc
        RuntimeError: foo
        """
                )
            )
            .replace(r'\{line\}', r'\d+')
            .replace(r'\{path\}', r'.*')
        )

        if platform.system() == 'Windows':
            expected = expected.replace(r'\/', r'\\')

        assert re.match(expected, trace), 'Traceback mismatch'


def test_invalid_event(env):
    """Invalid yield values will cause the simulation to fail."""

    def root(_):
        yield None

    env.process(root(env))
    with pytest.raises(RuntimeError, match='Invalid yield value "None"'):
        env.run()


def test_exception_handling(env):
    """If failed events are not defused (which is the default) the simulation
    crashes."""

    event = env.event()
    event.fail(RuntimeError())
    with pytest.raises(RuntimeError):
        env.run(until=1)


def test_callback_exception_handling(env):
    """Callbacks of events may handle exception by setting the ``defused``
    attribute of ``event`` to ``True``."""

    def callback(event):
        event.defused = True

    event = env.event()
    event.callbacks.append(callback)
    event.fail(RuntimeError())
    assert not event.defused, 'Event has been defused immediately'
    env.run(until=1)
    assert event.defused, 'Event has not been defused'


def test_process_exception_handling(env):
    """Processes can't ignore failed events and auto-handle exceptions."""

    def pem(_, event):
        try:
            yield event
            pytest.fail('Hey, the event should fail!')
        except RuntimeError:
            pass

    event = env.event()
    env.process(pem(env, event))
    event.fail(RuntimeError())

    assert not event.defused, 'Event has been defused immediately'
    env.run(until=1)
    assert event.defused, 'Event has not been defused'


def test_process_exception_chaining(env):
    """Because multiple processes can be waiting for an event, exceptions of
    failed events are copied before being thrown into a process. Otherwise, the
    traceback of the exception gets modified by a process.

    See https://bitbucket.org/simpy/simpy/issue/60 for more details."""
    import traceback

    def process_a(event):
        try:
            yield event
        except RuntimeError:
            stacktrace = traceback.format_exc()
            assert 'process_b' not in stacktrace

    def process_b(event):
        try:
            yield event
        except RuntimeError:
            stacktrace = traceback.format_exc()
            assert 'process_a' not in stacktrace

    event = env.event()
    event.fail(RuntimeError('foo'))

    env.process(process_a(event))
    env.process(process_b(event))

    env.run()


def test_sys_excepthook(env):
    """Check that the default exception hook reports exception chains."""

    def process_a(event):
        yield event

    def process_b(event):
        yield event

    event = env.event()
    event.fail(RuntimeError('foo'))

    env.process(process_b(env.process(process_a(event))))

    try:
        env.run()
    except BaseException:
        # Let the default exception hook print the traceback to the redirected
        # standard error channel.
        import sys
        from io import StringIO

        stderr, sys.stderr = sys.stderr, StringIO()

        typ, e, tb = sys.exc_info()
        assert typ is not None
        assert e is not None
        sys.excepthook(typ, e, tb)

        traceback = sys.stderr.getvalue()

        sys.stderr = stderr

        # Check if frames of process_a and process_b are visible in the
        # traceback.
        assert 'process_a' in traceback
        assert 'process_b' in traceback
