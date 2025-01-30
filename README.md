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
    一个资源核心是put, get方法.
    但是资源的容量是有限的.如果put,get过多.比如上来put十万个.容量只有10.那么我们的设计还是要把十万个
    put请求都记录下来.所以资源的设计还有一个put_queue, get_queue.
    当我们put_event被创造时候我们要去put_queue看一下.如果put_queue里面有东西,那么我们就处理一下, 把能put的put了. 还有我们get event被处理时候也一样.



    理解一下这个.
    def _trigger_put(self, get_event: Optional[GetType]) -> None:
        """This method is called once a new put event has been created or a get
        event has been processed.  这个方法被调用: 一种情况是一个put event被创造时, 或者一个get event被处理时.  这个函数用来迭代全部的put 事件, 看put事件的条件是否符合. 因为当put被创造时候我们就需要看看put_queue里面的东西是否可以被触发, 能触发的触发一下. 同理, get事件 被触发时候也要,先处理一下put queue里面的是否可以触发的触发一下.





下面这3个子类:
simpy-master/src/simpy/resources/container.py
resource.py
store.py

generator:
    1. send(value)
    功能：向生成器发送一个值，并恢复其执行直到下一个yield表达式。该值将成为yield表达式的结果。
    参数：value是发送给生成器的值。
    返回值：返回生成器中yield表达式的结果（如果有的话）。
    异常：如果生成器已经终止（例如，由于StopIteration或异常），则调用send()将引发StopIteration或相应的异常。

    2. close()
    功能：关闭生成器，使其不再产生任何值。如果生成器尚未终止，则调用close()将引发GeneratorExit异常到生成器中。生成器可以选择捕获此异常并执行清理操作。

    3. throw(type[, value[, traceback]])
    功能：将指定的异常抛入生成器中，并在生成器内部引发。如果生成器未捕获该异常，则它将传播到调用者。
    参数：
    type：异常的类型。
    value（可选）：异常的实例。如果没有提供，则使用type()创建一个新的实例。
    traceback（可选）：一个traceback对象，用于表示异常的堆栈跟踪。通常不需要手动提供。
    返回值：如果生成器捕获并处理了异常，则返回生成器中yield表达式的结果（如果有的话）。否则，传播异常。


# simpy_demo
"# simpy_demo" 
