from threading import Thread
from time import sleep
import uuid

class WaitThread(Thread):
    '''

    '''
    def __init__(self, time_to_wait, functionToRun, args_for_function, update_Thread_for_User, verbose = False):
        Thread.__init__(self)
        self.time = time_to_wait
        self.functionToRun = functionToRun
        self.args = args_for_function
        self.verbose = verbose
        self.update_Thread_for_User = update_Thread_for_User
        self.allowed = True

        if self.verbose: print('Made Thread')

        #If the thread was spawned by a user, we should update the user
        #storing that the user has spawned a thread
        if self.update_Thread_for_User:
            self.allowed = self.update_Thread_for_User(increase = True, verbose = self.verbose)
            if (not self.allowed):
                if verbose: print('The thread knows it is not allowed to spawn another thread')



    def run(self):
        if not self.allowed:
            del self
            return
        if self.verbose: print ('Timer started ...')
        sleep(self.time)
        self.functionToRun(*self.args)
        if self.verbose: print ('Timer ended and function performed')
        if self.update_Thread_for_User:
            self.update_Thread_for_User(increase = False, verbose = self.verbose)
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
