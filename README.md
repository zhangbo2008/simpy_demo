1-29.py是官方的demo都加了注释.
2025-01-30,0点22 开始搞源码.
太晚了睡了.

#一些其他资源:
__ http://docs.python.org/3/glossary.html#term-generator
__ https://simpy.readthedocs.io/en/latest/
__ https://simpy.readthedocs.io/en/latest/simpy_intro/index.html
__ https://simpy.readthedocs.io/en/latest/topical_guides/index.html
__ https://simpy.readthedocs.io/en/latest/examples/index.html
__ https://simpy.readthedocs.io/en/latest/api_reference/index.html
__ https://groups.google.com/forum/#!forum/python-simpy
__ https://www.youtube.com/watch?v=Bk91DoAEcjY
__ http://stefan.sofa-rockers.org/downloads/simpy-ep14.pdf

#整源码:
simpy-master/src/simpy/__init__.py
    这个代码把所有常用的部分放到一个命名空间里面了.如果你需要其他的你可以自己引用相关库包的地址.

simpy-master/src/simpy/core.py
    核心有2个函数一个step单步执行, 一个run一直执行,每次调用step
    step核心是197行,执行每一个事件的回调, 这里面回调的概念就是事件里面具体干了什么事.
    比如run里面until一个事件,那么会244行注册一个StopSimulation事件,然后197行时候到时间会触发这个时间的运行逻辑85行,然后这里面会给类一个传参,传的value会记录在对象的args属性里面.最终256行会结束这个模拟并且拿到这个值.

simpy-master/src/simpy/util.py
    2个触发函数

simpy-master/src/simpy/rt.py
    realTime的处理逻辑


simpy-master/src/simpy/exceptions.py
    interupt的异常, 他就一个属性cause

simpy-master/src/simpy/events.py
    最核心的事件.

simpy-master/src/simpy/resources/base.py
    资源的父类而我们使用的是她的子类.
下面这3个子类:
simpy-master/src/simpy/resources/container.py
resource.py
store.py






# simpy_demo
"# simpy_demo" 
