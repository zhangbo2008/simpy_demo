# 理解yield

#encoding:UTF-8  
def yield_test(n):  
    for i in range(n):  
        print('开始yield')
        yield call(i)  
        print("i=",i)  
    #做一些其它的事情      
    print("do something.")      
    print("end.")  

def call(i):  
    return i*2  

#使用for循环  
for i in yield_test(5):  
    print(i,",")
a=yield_test(5)
print(next(a),'打印next')    
print(next(a),'打印next2')    
# 总结: yield 放在函数里面. 这样函数调用时候就会卡在yield上. 也就是运行完yield的上一行. 然后yield 是出让的意思, 把cpu让给别人跑, 而他自己在等待next函数的调用. next函数效果是从yield行开始运行, 运行到函数下一次yield之前.说白了也就是拿回cpu控制权进行代码执行. 当遇到下一次yield再次出让.
    