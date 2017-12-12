import uuid
from threading import RLock

class User:
    def __init__(self, sid, name = ''):
        '''
        Each user is allowed to spawn nrOfThreadsAllowed threads.
        '''
        self.sid = sid
        self.name = name
        self.nrOfSidUpdates = 0
        self.uniqueID = uuid.uuid4().hex
        self.lock = RLock()
        self.nrOfThreadsSpawned = 0
        self.nrOfThreadsAllowed = 1

    def add_Name(self, name):
        self.name = name

    def update_Sid(self, sid):
        self.sid = sid
        self.nrOfSidUpdates

    def update_Thread_Number(self, increase, verbose = False):
        with self.lock:
            if self.nrOfThreadsSpawned >= self.nrOfThreadsAllowed and increase:
                if verbose: print('User {} is not allowed to spawn another thread'.format(self.name))
                return False
            elif increase:
                if verbose: print('User {} just spawned a thread'.format(self.name))
                self.nrOfThreadsSpawned += 1
                return True
            else:
                if verbose: print('User {} just removed a thread'.format(self.name))
                self.nrOfThreadsSpawned -= 1
                return True


class Clients:
    def __init__(self):
        self.users = []
        self.nrOfClients = 0

    def add_User(self, sid, name = ''):
        user = User(sid,name)
        self.users.append(user)
        self.nrOfClients += 1
        return user

    def removeUser(self, name):
        for i in range(self.users):
            if self.users[i].name == name:
                del self.users[i]
                nrOfClients -= 1

    def find_User_By_uniqueID(self, uniqueID):
        for u in self.users:
            if u.uniqueID == uniqueID:
                return u
        return None

    def find_User_By_Name(self, name):
        for u in self.users:
            if u.name == name:
                return u
        return None

    def find_User_By_Sid(self, sid):
        for u in self.users:
            if u.sid == sid:
                return u
        return None

    def __str__(self):
        ret = ''
        ret+=('_________________CLIENTS_____________\n')
        for u in self.users:
            ret+=('-------------------------------------\n')
            ret+=('User name: {}\n'.format(u.name))
            ret+=('SID: {}\n'.format(u.sid))
            ret+=('UniqueID: {}\n'.format(u.uniqueID))
            ret+=('Nr. threads: {}\n'.format(u.nrOfThreadsSpawned))
            ret+=('_____________________________________')

        return ret
