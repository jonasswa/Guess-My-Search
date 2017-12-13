from ClientStorage import User

class Player:

    def __init__(self, name, userObject, gameObject):
        self.name = name
        self.gameObject = gameObject
        self.userObject = userObject

        userObject.name = name
        userObject.gameObject = gameObject
        userObject.playerObject = self


class Game:

    def __init__(self, gameName, timePerRound=10, nrOfRounds=5):
        self.timePerRound = timePerRound
        self.nrOfRounds = nrOfRounds

        self.currentRound = 0
        self.gameStarted = False
        self.gameName = gameName
        self.players = []

    def getPlayerNames(self):
        ret = []
        for player in self.players:
            ret.append(player.name)
        return ret

    def add_Player(self, name, userObject, verbose = False):
        if self.find_Player_By_Name(name):
            if verbose: print('In GAME:add_Player: player EXISTS')
            return None

        if verbose: print('In GAME:add_Player: A new player was made')
        player = Player(name, userObject, self)
        self.players.append(player)
        return player

    def remove_Player(self, name, verbose = False):
        player = self.find_Player_By_Name(name)

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
