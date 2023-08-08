# We need to import the enum class
import threading, time, uuid
from enum import Enum
from collections import deque

class TaskAnnotation(Enum):
    TRANSPORTATION = 0
    STORAGE = 1
    PROCESSING = 2
    QUALITY_CONTROL = 3
    PACKAGING = 4
    DISTRIBUTION = 5

class TaskState(Enum):
    WAITING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3
    RETRY = 4
    RETRYING = 5

class DeliverType(Enum):
    NO_DELIVERY = 0
    DELIVER_ON_TIME = 1
    DELIVER_ON_UNIT = 2

class Timer(object):
    def __init__(self, interval, trigger=None):
        self.trigger = trigger
        self.interval = interval
        self.timer_thread = None
        self.tick_hooks = []
        self.round = 0
        self.done = False

    def start(self):
        self.timer_thread = threading.Thread(target=self.tick)
        self.timer_thread.start()

    def tick(self):
        while True:
            if self.done:
                for hook in self.tick_hooks:
                    hook.on_done()
                break
            self.round += 1
            if self.trigger:
                self.trigger(self.round)
            for hook in self.tick_hooks:
                hook.on_tick()
            time.sleep(self.interval)

    def stop(self):
        self.timer_thread.join()

    def register_hook(self, hook):
        if hook not in self.tick_hooks:
            self.tick_hooks.append(hook)

class BaseTask(object):
    def __init__(self, name, second_capacity, uses_resources=None, timer=None, stack_limit=100):
        self.name = name
        self.second_capacity = second_capacity
        self.timer = timer
        self.timer.register_hook(self)
        self.id = uuid.uuid4()
        self.task_status = TaskState.WAITING
        self.stack = 0
        self.stack_limit = stack_limit
        # self.deliver_type = DeliverType.NO_DELIVERY
        # self.deliver_on_unit = 0
        # self.deliver_on_time = 0
        self.snapshot = deque(maxlen=2)
        self.uses_resources = uses_resources
        self.staging = {}
        self.tick_total = 0
        self.tick_working = 0

    def on_tick(self):
        self.tick_total += 1
        self.__take_snapshot()
        self.__is_snapshot_changed()
        if self.__stack_available() and self.__fetch_resources():
            self.tick_working += 1
            self.__produce()

    def on_done(self):
        print(f'{self.name} performance: \t {self.tick_working / self.tick_total} working.')

    def start_task(self):
        self.task_status = TaskState.RUNNING

    def append_stack(self, amount):
        if self.stack + amount > self.stack_limit:
            self.stack = self.stack_limit
            print(f'{self.name}: \t stack limit reached.')
        else:
            self.stack += amount

    def __fetch_resources(self):
        if self.uses_resources:
            available_resources = [resource for resource in self.uses_resources if resource[0].stack >= resource[1] * self.second_capacity]
            if len(available_resources) == len(self.uses_resources):
                for resource in available_resources:
                    res = resource[0]
                    amount = resource[1] * self.second_capacity
                    res.output(amount)
                return True
            else:
                print(f'{self.name}: \t not enough resources.')
                return False
        return False
    
    def __stack_available(self):
        return self.stack + self.second_capacity <= self.stack_limit
    
    def __produce(self):
        self.append_stack(self.second_capacity)

    def output(self, amount):
        if self.stack < amount:
            print(f'{self.name}: \t not enough stack.')
            return False
        else:
            self.stack -= amount
            return True

    def __is_snapshot_changed(self):
        if len(self.snapshot) < self.snapshot.maxlen:
            return
        else:
            current_snapshot = self.snapshot[-1]
            last_snapshot = self.snapshot[-2]
            difference = {k: current_snapshot[k] for k in current_snapshot if current_snapshot[k] != last_snapshot[k]}
            for k in difference:
                print(f'{self.name}: \t {k} changed from {last_snapshot[k]} to {current_snapshot[k]}')

    def __take_snapshot(self):
        self.snapshot.append({
            'name': self.name,
            'second_capacity': self.second_capacity,
            'task_status': self.task_status,
            'stack': self.stack,
            'stack_limit': self.stack_limit,
        })

    def __str__(self):
        return self.name
    