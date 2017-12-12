import uuid

class User:
    def __init__(self, sid, name = ''):
        self.sid = sid
        self.name = name
        self.nrOfSidUpdates = 0
        self.uniqueID = uuid.uuid4().hex

    def add_Name(self, name):
        self.name = name

    def update_Sid(self, sid):
        self.sid = sid
        self.nrOfSidUpdates

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
        for u in users:
            if u.sid == sid:
                return u
        return None
