from threading import Thread
from time import sleep
import uuid

class WaitThread(Thread):
    def __init__(self, time_to_wait, functionToRun, args_for_function, verbose = False):
        Thread.__init__(self)
        self.time = time_to_wait
        self.functionToRun = functionToRun
        self.args = args_for_function
        self.verbose = verbose
        if self.verbose: print('Made Thread')

    def run(self):
        if self.verbose: print ('Timer started ...')
        sleep(self.time)
        self.functionToRun(*self.args)
        if self.verbose: print ('Timer ended and function performed')
        return

if __name__ == "__main__":
    from threading import RLock
    def f(a,b,c, lock):
        with lock:
            print(a,b,c)

    lock = RLock()
    thread = WaitThread(3, f, (1,2,3, lock), verbose = True)
    thread.start()
    f('This is before','the','other function',lock)
