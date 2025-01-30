"""
The ``simpy`` module aggregates SimPy's most used components into a single
namespace. This is purely for convenience. You can of course also access
everything (and more!) via their actual submodules.

The following tables list all the available components in this module.

{toc}

"""

from __future__ import annotations

import importlib.metadata
from typing import Tuple, Type

from simpy.core import Environment
from simpy.events import AllOf, AnyOf, Event, Process, Timeout
from simpy.exceptions import Interrupt, SimPyException
from simpy.resources.container import Container
from simpy.resources.resource import PreemptiveResource, PriorityResource, Resource
from simpy.resources.store import FilterStore, PriorityItem, PriorityStore, Store
from simpy.rt import RealtimeEnvironment
#======首先我们定义all这个数组,他把这个模块内所有组件的名字都写进去了.
__all__ = [
    'AllOf',
    'AnyOf',
    'Container',
    'Environment',
    'Event',
    'FilterStore',
    'Interrupt',
    'PreemptiveResource',
    'PriorityItem',
    'PriorityResource',
    'PriorityStore',
    'Process',
    'RealtimeEnvironment',
    'Resource',
    'SimPyException',
    'Store',
    'Timeout',
]

#==只是生成文档用的.把上面组件.
def _compile_toc(
    entries: Tuple[Tuple[str, Tuple[Type, ...]], ...],
    section_marker: str = '=',
) -> str:
    """Compiles a list of sections with objects into sphinx formatted
    autosummary directives."""
    toc = ''
    for section, objs in entries:
        toc += '\n\n'
        toc += f'{section}\n'
        toc += f'{section_marker * len(section)}\n\n'
        toc += '.. autosummary::\n\n'
        for obj in objs:
            toc += f'    ~{obj.__module__}.{obj.__name__}\n'
    return toc

#这个是被生成文档的对象全体.是一个二维数组.
_toc = (
    (
        'Environments',
        (
            Environment,
            RealtimeEnvironment,
        ),
    ),
    (
        'Events',
        (
            Event,
            Timeout,
            Process,
            AllOf,
            AnyOf,
            Interrupt,
        ),
    ),
    (
        'Resources',
        (
            Resource,
            PriorityResource,
            PreemptiveResource,
            Container,
            Store,
            PriorityItem,
            PriorityStore,
            FilterStore,
        ),
    ),
    ('Exceptions', (SimPyException, Interrupt)),
)
#使用上面命令生成文档,动态的
# Use the _toc to keep the documentation and the implementation in sync.
if __doc__:
    __doc__ = __doc__.format(toc=_compile_toc(_toc))
    assert set(__all__) == {obj.__name__ for _, objs in _toc for obj in objs}

try:
    __version__ = importlib.metadata.version('simpy') #尝试找到version来写入版本信息, 如果没找到也pass, 无所谓.
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    pass
