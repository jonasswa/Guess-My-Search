from ClientStorage import User
from time import gmtime, strftime
from threading import RLock
from utilslib import getAutoComplete

class Entry:

    def __init__(self, searchString, autoComplete, number, playerObject):
        self.searchString = searchString
        self.autoComplete = autoComplete
        self.playerObject = playerObject
        self.googleAutocompletes = getAutoComplete(search_input=searchString)
        self.nr = number

        self.otherAutocompletes = []

    def addOtherAutocomplete(self, autoComplete, playerObject):
        self.otherAutocompletes.append(self.OuterAutocomplete(autoComplete, playerObject))

    class OuterAutocomplete:

        def __init__(self, autoComplete, playerObject):
            self.autoComplete = autoComplete
            self.playerObject = playerObject
            self.votes = 0


class Player:

    def __init__(self, name, userObject, gameObject):
        self.name = name
        self.gameObject = gameObject
        self.userObject = userObject
        self.ready = False
        self.points = 0

        userObject.name = name
        userObject.gameObject = gameObject
        userObject.playerObject = self

        self.entry = None

    def set_Entry(self, searchString, autoComplete, nrOfEntry):
        self.entry = Entry(searchString, autoComplete, nrOfEntry, self)
        return self.entry

    def __str__(self):
        return self.name

class ChatMmsg:

    def __init__(self, msg, player):
        self.msg = msg
        if len(self.msg)>800:
            self.msg = self.msg[0:10]

        self.player = str(player)
        self.timeStamp = strftime("%H:%M:%S", gmtime())

    def __str__(self):
        return self.player + ': ' + self.msg

    def get_Player_And_Msg(self):
        return self.player, self.msg

class Game:

    def __init__(self, gameName, timePerRound=10, nrOfRounds=5):
        self.timePerRound = timePerRound
        self.nrOfRounds = int(nrOfRounds)
        self.currentRound = 1
        self._roundCycle = ['roundStart', 'roundSupply', 'roundVote', 'roundEnd']
        self._stageIndex = 0
        self.gameStarted = False
        self.gameName = gameName
        self.players = []
        self.chatMessages = []
        self.lock = RLock()

        self.spawnedThread = None
        self.nrOfEntry = 0
        self.entries = []

        self.roundEnded = False
        self.supplyEnded = False

        self.nrOfSupply = 0

    def get_Nr_Of_Players(self):
        return (len(self.players))

    def go_To_Next_Stage(self):
        self._stageIndex += 1
        if (self._stageIndex >= len(self._roundCycle)):
            self._stageIndex = 0
            self.currentRound += 1
            self.roundEnded = False
            self.supplyEnded = False

    def end_Stage(self):
        with self.lock:
            if self.get_Stage() =='roundStart' and not(self.roundEnded):
                print("Ending round start")
                self.roundEnded = True
                self.go_To_Next_Stage()
                return

            if self.get_Stage() == 'roundSupply' and not(self.supplyEnded):
                print("Ending round supply")
                self.supplyEnded = True
                self.go_To_Next_Stage()
                return

    def get_Stage(self):
        if self.gameStarted == False:
            return 'lobby'
        if self.currentRound >= self.nrOfRounds:
            return 'gameSummary'
            self._stageIndex = 0
        return self._roundCycle[self._stageIndex]

    def get_Player_Names(self):
        ret = []
        for player in self.players:
            ret.append(player.name)
        return ret

    def get_Player_Names_And_Status(self):
        ret = []
        for player in self.players:

            if player.ready:
                entry = '[✓] '
            else:
                entry = '[✗] '

            entry += player.name

            ret.append(entry)
        return ret

    def add_Entry(self, searchString, autoComplete, player):
        entry = player.set_Entry(searchString, autoComplete, self.nrOfEntry)
        self.entries.append(entry)
        self.nrOfEntry += 1

    def get_Search_Strings(self, playerObject):
        ret = []

        for entry in self.entries:
            if (entry.playerObject == playerObject):
                ret.append(None)
            else:
                ret.append(entry.searchString)

        return ret

    def get_Autocomplete_List(self, playerObject):
        '''
        The ret[[0,1], ...] is always the creators autocomplete, and
        the googles autocolpete; in that order.
        '''
        ret = [[]]
        for entry in self.entries:
            if (entry.playerObject == playerObject):
                ret.append([None])
            else:
                ret.append(entry.autoComplete)
                ret.append(entry.googleAutocompletes[0])
                for autcomplete in entry.otherAutocompletes:
                    ret.append([autcomplete.autoComplete])
        return ret


    def reset_Players_Ready(self):
        for player in self.players:
            player.ready = False
        return

    def all_Players_Ready(self):
        for player in self.players:
            if (not player.ready):
                return False

        return True

    def add_Chat_Msg(self, chatMsg, playerName):
        self.chatMessages.insert(0, ChatMmsg(msg=chatMsg, player=playerName))
        if len(self.chatMessages)>10:
            del self.chatMessages[-1]

    def add_Player(self, name, userObject, verbose = False):
        if self.find_Player_By_Name(name):
            if verbose: print('In GAME:add_Player: player name EXISTS')
            return None

        if verbose: print('In GAME:add_Player: A new player was made')
        player = Player(name, userObject, self)
        self.players.append(player)
        return player

    def remove_Player_By_User_Object(self, userObj, verbose = False):
        player = self.find_Player_By_User_Object(userObj)

        if (not player):
            if verbose: print('In GAME:remove_Player: player not found')
            return

        self.players.remove(player)
        if verbose: print('In GAME:remove_Player: player removed')

    def find_Player_By_Name(self, name):
        for p in self.players:
            if p.name == name:
                return p

        return None

    def find_Player_By_User_Object(self, userObj):
        for p in self.players:
            if p.userObject == userObj:
                return p
        return None

class GameContainter:

    def __init__(self):

        self._games = []

    def add_Game(self, gameName, timePerRound=10, nrOfRounds=5, verbose = False):

        counter = 1
        newGameName = gameName
        while (self.find_Game_By_Name(newGameName, verbose = verbose)):
            newGameName = gameName + str(counter)
            counter += 1
        game = Game(newGameName, timePerRound, nrOfRounds)
        self._games.append(game)
        return game

    def find_Game_By_Name(self, gameName, verbose = False):
        for game in self._games:
            if game.gameName == gameName:
                if verbose: print('In GameContainter:find_Game_By_Name: Game found')
                return game
        if verbose: print('In GameContainter:find_Game_By_Name: Game NOT found')
        return None

    def removeGame(self,game, verbose = False):
        try:
            self._games.remove(game)
            if verbose: print('In ClientList:removeGame: Removed game')
        except:
            if verbose: print('In ClientList:removeGame: Could not find game in clientList')

    def __str__(self):
        ret = ''
        ret+='\nGAMINFO:\n'
        for game in self._games:
            ret+=('gameName: {}\n'.format(game.gameName))
            ret+=('timePerRound: {}\n'.format(game.timePerRound))
            ret+=('nrOfRounds: {}\n'.format(game.nrOfRounds))
            ret+=('currentRound: {}\n'.format(game.currentRound))
            ret+=('gameStarted: {}\n'.format(game.gameStarted))
            ret+=('players: {}\n\n'.format(game.players))
        ret+=('_____________________________')

        return ret


if __name__=="_main__":
    hanna = 1
    hanna = "Hanna"

    hanna = Game(gameName="Spillet", timePerRound=10, nrOfRounds=5)
