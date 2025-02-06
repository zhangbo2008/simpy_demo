# 2025-01-31,19点14 继续研究其他架构的离散仿真.


import heapq  # 导入heapq模块用于实现最小堆，以存储和排序事件

class Event:
    def __init__(self, time, customer_id, action):
        self.time = time
        self.customer_id = customer_id
        self.action = action

    def __lt__(self, other):
        return self.time < other.time

def simulate(arrival_rate, service_time, simulation_time):
    events = []  # 存储事件的列表
    time = 0  # 当前时间
    customers = 0  # 当前顾客数
    waiting_customers = 0  # 等待的顾客数

    # 初始化：添加第一个顾客到达事件
    heapq.heappush(events, Event(time, customers, 'arrival'))
    customers += 1

    while events and time < simulation_time:
        # 取出并处理下一个事件
        event = heapq.heappop(events)
        time = event.time

        if event.action == 'arrival':
            print(f"{time}: 顾客{event.customer_id}到达，等待顾客数：{waiting_customers + 1}")
            waiting_customers += 1

            # 生成下一个顾客到达事件
            next_arrival_time = time + 1 / arrival_rate
            heapq.heappush(events, Event(next_arrival_time, customers, 'arrival'))
            customers += 1

            # 如果服务台空闲，则处理等待队列中的第一个顾客
            if waiting_customers > 0:
                next_service_time = time + service_time
                heapq.heappush(events, Event(next_service_time, event.customer_id, 'service'))
                waiting_customers -= 1

        elif event.action == 'service':
            print(f"{time}: 顾客{event.customer_id}开始服务")
            # 服务完成后，无需添加新事件

    print(f"模拟结束，总顾客数：{customers}")

# 示例：模拟到达率为每分钟1人，服务时间为3分钟，模拟时间为10分钟的银行排队系统
simulate(1, 3, 10)
