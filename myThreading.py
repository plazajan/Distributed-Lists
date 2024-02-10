# Jan Plaza
# May 23, 2020

import threading
import time
import logging

#=====================================

THREAD_TIME = True
if hasattr(time, 'thread_time_ns'): 
    def threadTime(): # Python 3.7 on Linux
        """The sum of the system and user CPU time of the current thread. 
           It does not include time elapsed during sleep."""
        return time.thread_time_ns()
elif hasattr(time, 'clock_gettime_ns') and hassattr(time, 'CLOCK_THREAD_CPUTIME_ID'):
    def threadTime(): # Python 3.3 on Linux
        """Thread-specific CPU-time clock."""
        return time.clock_gettime_ns(time.CLOCK_THREAD_CPUTIME_ID)
else:
    def threadTime():
        pass
    THREAD_TIME = False

# Is  time.thread_time_ns()  the same as
# time.clock_gettime_ns(time.CLOCK_THREAD_CPUTIME_ID) ?
#=====================================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(threadName)-10s %(message)s',
)
# usage: logging.debug('myMessageString')

if THREAD_TIME:
    def threadLog(operation, argument, t):
        logging.debug(
            "{:4} {:>2} took {:>9} ns.".format(
                operation, str(argument), str(threadTime() - t)))
else:
    def threadLog(operation, argument, t):
        logging.debug("{:4} {:>2}".format(operation, str(argument)))

# usage:
# t = threadTime()
# ...
# threadLog("...", ..., t)
# for instance, threadLog("push", self.data, t)

#=====================================

class EventPlus:
    """One can wait for an EventPlus object to be set True
       but also to be set False (cleared), unlike with threading.Event.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.lock.acquire()
        self.et = threading.Event()
        self.ef = threading.Event()
        self.et.clear() # self is an event with value False.
        self.ef.set() # ef must always be the opposite of et.
        self.lock.release() # ef and et are reset in an indivisble operation.
        
    def setTrue(self): 
        self.lock.acquire()
        self.et.set()
        self.ef.clear() 
        self.lock.release()

    def setFalse(self):
        self.lock.acquire()
        self.et.clear()
        self.ef.set() 
        self.lock.release()

    def isTrue(self):
        return self.et.isSet()

    def isFalse(self):
        return self.ef.isSet()

    def waitForTrue(self):
        self.et.wait()

    def waitForFalse(self):
        self.ef.wait()

#=====================================

class AnyType(object):
    """Similar to NoneType. There is only one object of this type: Any. 
       However, the object raises a TypeError
       when used in a Boolean context or compared using == or !=.
       Any == Any --> TypeError
       Any is Any --> True
       """
    
    def __new__(cls, *args, **kwargs):
        # singleton (only one such objects exists)
        try:
            obj = cls._obj
        except AttributeError:
            obj = object.__new__(cls, *args, **kwargs)
            cls._obj = obj
        return obj

    def __bool__(self):
        raise TypeError("The object Any is neither True nor False.")

    def __eq__(self, other):
        raise TypeError("The object Any cannot be compared (==) to anything.")

    def __ne__(self, other):
        raise TypeError("The object Any cannot be compared (!=) to anything.")

    def __repr__(self):
        return "Any"

Any = AnyType()

#=====================================

def main():
    a = AnyType()
    b = AnyType()
    print(a is b)  # True
    print(a)       # Any
    try:  
        print(10 == a) # False
    except TypeError as err:
        print("TypeError. {0}".format(err))
    try:    
        print(10 != a) # True
    except TypeError as err:
        print("TypeError. {0}".format(err))
    try:    
        print(a == 10) # False
    except TypeError as err:
        print("TypeError. {0}".format(err))
    try:    
        print(a != 10) # True
    except TypeError as err:
        print("TypeError. {0}".format(err))
    try:    
        print(a != b)  # False
    except TypeError as err:
        print("TypeError. {0}".format(err))
    try:    
        print(a == b)  # True
    except TypeError as err:
        print("TypeError. {0}".format(err))    
    try:
        if a:
            print("hello")
    except TypeError as err:
        print("TypeError. {0}".format(err))   
    try:
        print(a or True)
    except TypeError as err:
        print("TypeError. {0}".format(err))

#=====================================
    
if __name__ == "__main__":
    main()

#=====================================


