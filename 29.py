"""
Event Latency example

Covers:

- Resources: Store

Scenario:
  This example shows how to separate the time delay of events between
  processes from the processes themselves.

When Useful:
  When modeling physical things such as cables, RF propagation, etc.  it
  better encapsulation to keep this propagation mechanism outside of the
  sending and receiving processes.

  Can also be used to interconnect processes sending messages

Example by:
  Keith Smith

"""

import simpy

SIM_DURATION = 100


class Cable:
    """This class represents the propagation through a cable."""

    def __init__(self, env, delay):
        self.env = env
        self.delay = delay
        self.store = simpy.Store(env)

    def latency(self, value):
        yield self.env.timeout(self.delay)
        self.store.put(value)

    def put(self, value): # put是带延迟的放.
        self.env.process(self.latency(value))

    def get(self):
        return self.store.get()


def sender(env, cable):
    """A process which randomly generates messages."""
    while True:
        # wait for next transmission
        yield env.timeout(5)
        cable.put(f'Sender sent this at {env.now}')


def receiver(env, cable):
    """A process which consumes messages."""
    while True:
        # Get event for message pipe
        msg = yield cable.get()
        print(f'Received this at {env.now} while {msg}')


# Setup and start the simulation
print('Event Latency')
env = simpy.Environment()

cable = Cable(env, 10)
env.process(sender(env, cable))
env.process(receiver(env, cable))

env.run(until=SIM_DURATION)