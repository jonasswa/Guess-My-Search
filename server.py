from flask_socketio import SocketIO
from flask import Flask, make_response, request, session
from flask import render_template, session, url_for, redirect

from threading import RLock

from threading import Thread
from time import sleep
from ClientStorage import Clients, User
from gameObjects import Game, GameContainter, Player, ChatMmsg

from random import shuffle

#Init server
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'lskwod=91230?=)ASD?=)("")@'
socketio = SocketIO(app, async_mode='threading')

timerLock = RLock()
asyncLock = RLock()
clients = Clients()

games = GameContainter()

debugging = True

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def index():
    verbose = (False or debugging)
    error = request.args.get('error')
    return make_response(render_template('makeGame.html', title = "Welcome", cool = 123, error = error))

@app.route('/gameRoom', methods = ['POST', 'GET'])
def gameRoom():
    global games
    verbose = (False or debugging)
    argumentsMakeGame = ['name', 'gameName', 'nrOfRounds', 'time', 'newGame']
    argumentsJoinGame = ['name', 'gameName', 'newGame']

    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)

    if (not user):
        return redirect(url_for('index') + '?error=No user. Refreshing')

    if (not user.gameObject):
        data = request.form
        #MAKE A NEW GAME
        if data['newGame'] == 'yes':
            if verbose: print('In server:gameRoom() nrOfRounds set!')
            for key in data.keys():
                argumentsMakeGame.remove(key)
            if argumentsMakeGame:
                return redirect(url_for('index') + '?error=Not enough arguments when creating the game')
            if verbose: print('In server:gameRoom() arguments needed for making a game are present')
            #Creating player and game
            game = games.add_Game(gameName=data['gameName'], nrOfRounds=data['nrOfRounds'], timePerRound=data['time'])
            player = game.add_Player(name=data['name'], userObject=user)
            if (not player):
                return redirect(url_for('index') + '?error=Player name already exists in this game...')
            if verbose: print('In server:gameRoom() game created with the name {} and user/player added'.format(game.gameName))

        #Join an existing game
        else:
            data = request.form
            if verbose: print('In server:gameRoom() joining a game!')
            for key in data.keys():
                argumentsJoinGame.remove(key)
            if argumentsJoinGame:
                return redirect(url_for('index') + '?error=Not enough arguments when joining the game')

            if verbose: print('In server:gameRoom() Searching for game: {}'.format(data['gameName']))
            #Check if game exists
            game = games.find_Game_By_Name(data['gameName'], verbose)
            if (not game):
                if verbose: print('The game was not found')
                return redirect(url_for('index') + '?error=Game not found')
            #Check if name already taken
            for player in game.players:
                if player.name == data['name']:
                    return redirect(url_for('index') + '?error=Name already taken')
            player = game.add_Player(name=data['name'], userObject=user)
            if verbose: print('In server:gameRoom() Player joined game')

            if verbose: print('In server:gameRoom() game created and user/player added')
            sendMessageToGame(game, '{} joined the game'.format(data['name']))
            emitToGame(game = game, arg = ('refresh_Player_List',{}), lock = timerLock)


    else:
        if verbose: print('User alreade in game')

    error = None
    return make_response(render_template('gameRoom.html', title = "Game Room", gameName = user.gameObject.gameName, error = error))



@app.route('/gameRoomContent')
def gameRoomContent():
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)

    if userNotComplete(user, verbose = (False or debugging)):
         return 'ERROR: Something strange happened. Please leave game and rejoin'

    game = user.gameObject
    nrOfRounds = game.nrOfRounds
    timePerRound = game.timePerRound
    gameName = game.gameName
    roundNr = game.currentRound

    if (user.gameObject.get_Stage() == 'lobby'):
        return render_template('lobbyContent.html',
                                gameName = gameName,
                                nrOfRounds = nrOfRounds,
                                timePerRound = timePerRound)

    elif (user.gameObject.get_Stage() == 'roundStart'):
        return render_template('roundContentStart.html',
                                timePerRound = timePerRound,
                                roundNr = roundNr,
                                nrOfRounds = nrOfRounds)

    elif (user.gameObject.get_Stage() == 'roundSupply'):
        game.spawnedThread = None
        game.reset_Players_Ready()

        emitToGame(game = game, arg = ('refresh_Player_List',{}), lock = timerLock)
        print('GameContent:')
        print(game.get_Search_Strings(user.playerObject))
        return render_template('roundContentSupply.html',
                                nrOfPlayers = game.get_Nr_Of_Players(),
                                searchStrings = game.get_Search_Strings(user.playerObject),
                                nrOfEntries = game.nrOfEntry)

    elif (user.gameObject.get_Stage() == 'roundVote'):
            game.reset_Players_Ready()
            emitToGame(game = game, arg = ('refresh_Player_List',{}), lock = timerLock)
            return makeVoteContent(user)

    elif (user.gameObject.get_Stage() == 'roundEnd'):
            return render_template('roundContentEnd.html')

    elif (user.gameObject.get_Stage() == 'gameSummary'):
            return render_template('gameContentSummary.html')

def makeVoteContent(user):
    game = user.gameObject
    playerObject = user.playerObject

    autocompletes = game.get_Autocomplete_List(playerObject)

    print(autocompletes)

    return render_template('roundContentVote.html',
                            nrOfPlayers = game.get_Nr_Of_Players(),
                            nrOfEntries = game.nrOfEntry,
                            searchStrings = game.get_Search_Strings(user.playerObject),
                            autocompletes = autocompletes)

@app.route('/playerList')
def playerList():
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    verbose = (False or debugging)
    if userNotComplete(user, verbose = (False or debugging)):
        return redirect(url_for('index') + '?error=User not in game')

    playerList = user.gameObject.get_Player_Names_And_Status()
    if verbose: print('Got {} players'.format(len(playerList)))
    return render_template('playerList.html', playerList = playerList)


@app.route('/chatContent')
def chatContent():
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    if userNotComplete(user, verbose = (False or debugging)):
        return redirect(url_for('index') + '?error=User not in game')
    chat = user.gameObject.chatMessages
    msgs = []
    players = []

    for msg in chat:
        player, msg = msg.get_Player_And_Msg()
        msgs.append(str(msg))
        players.append(str(player))
    if players:
        players.reverse()
        msgs.reverse()

    return render_template('chat.html', players = players, chatMsg = msgs)


@app.route('/leave_Game')
def leaveGame():
    verbose = (False or debugging)

    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    if (not user):
        if verbose: print('No user')
        return redirect(url_for('index'))
    game = user.gameObject
    game.remove_Player_By_User_Object(user)
    name = user.playerObject.name
    user.resetUser()

    if len(game.players)<1:
        games.removeGame(game=game, verbose = verbose)
    else:
        emitToGame(game = game, arg = ('refresh_Player_List',{}), lock = timerLock)
        emitToGame(game = game, arg = ('client_warning',{'msg': name+' left the game'}), lock = timerLock)
    print (len(games._games))

    return redirect(url_for('index'))

@socketio.on('submit_entry')
def collectData(msg):
    verbose = (False or debugging)
    if verbose: print ('Entry reveived by the server')
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    if verbose: print ('User retrieved')
    if (not user):
        if verbose: print('No user found when collecting the data')
        return
    if user.playerObject.entry:
        if verbose: print('User already submitted.')
        return

    if verbose: print ('Setting entry for user')
    user.gameObject.add_Entry(msg['searchString'], msg['suggestion'], user.playerObject)
    if verbose: print('Got entry')

    if user.gameObject.nrOfEntry >= user.gameObject.get_Nr_Of_Players():
        emitToGame(game = user.gameObject, arg = ('refresh_div_content',{'div': 'entryList', 'cont': '/gameRoomContent'}), lock = timerLock)

@socketio.on('submit_supply')
def submitSupply(data):
    verbose = (True or debugging)
    if verbose: print ('Supply reveived by the server')
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    if verbose: print ('User found')
    if (not user):
        if verbose: print('No user found when collecting the data')
        return

    game = user.gameObject
    if verbose: print ('The data received is: {}'.format(data))

    if (not data):
        return

    if verbose: print('The actual data:')

    for key, value in data.items():
        if verbose: print('Key: {} \t Value: {}'.format(key, value))
        if value == '':
            continue
        game.entries[int(key)].addOtherAutocomplete(value, user.playerObject)

    game.nrOfSupply += 1

    if user.gameObject.nrOfSupply >= user.gameObject.get_Nr_Of_Players():
        emitToGame(game = user.gameObject, arg = ('refresh_div_content',{'div': 'contentVote', 'cont': '/gameRoomContent'}), lock = timerLock)


    if verbose:
        print('')
        for entry in game.entries:
            print('-------------------------------------------')
            print('The entry with the serch string: \t {}\nHas the following autocompletes added:'.format(entry.searchString))
            for supply in entry.otherAutocompletes:
                print (supply.autoComplete)
            print('-------------------------------------------')
        print('')

@socketio.on('toggle_ready')
def toggleReady(msg):
    verbose = (False or debugging)
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)

    if (not user):
        if verbose: print('No user found when toggling ready')
        return

    player = user.playerObject

    if (not player):
        if verbose: print('No player found for the user/client.')

    player.ready = not player.ready
    game = player.gameObject

    #A game object will always exist if there is a playerObject
    emitToGame(game = game, arg = ('refresh_Player_List',{}), lock = timerLock)
    playersReady = game.all_Players_Ready()

    print ('STAGE:', game.get_Stage())

    #Start round
    if playersReady and game.gameStarted == False and not game.spawnedThread:
        game.gameStarted = True
        game.reset_Players_Ready()
        emitToGame(game = game, arg = ('change_content', {'url':'/gameRoomContent'}), lock = timerLock)
        emitToGame(game = game, arg = ('client_message', {'msg':'Game started. Have fun!'}), lock = timerLock)

        #Start timer
        game.spawnedThread = RoundTimer(int(game.timePerRound), user)
        game.spawnedThread.start()
        return

    #End round
    if playersReady and game.get_Stage() == 'roundStart':
        if verbose: print ('Round ended by users')
        user.gameObject.end_Stage()
        game.reset_Players_Ready()
        if verbose: print('Current stage of game is: {}'.format(user.gameObject.get_Stage()))
        emitToGame(game = user.gameObject, arg = ('round_End', {}), lock = timerLock)
        emitToGame(game = user.gameObject, arg = ('client_message', {'msg':'Round ended'}), lock = timerLock)
        return

    #End supply
    if playersReady and game.get_Stage() == 'roundSupply':
        user.gameObject.end_Stage()
        game.reset_Players_Ready()
        emitToGame(game = user.gameObject, arg = ('supply_End', {'nrOfEntries': user.gameObject.nrOfEntry}), lock = timerLock)
        emitToGame(game = user.gameObject, arg = ('client_message', {'msg':'Round ended'}), lock = timerLock)
        return


class RoundTimer(Thread):

    def __init__(self, timeToWait, user):
         Thread.__init__(self)
         self.timeToWait = timeToWait
         self.user = user

    def run(self):

        sleep(self.timeToWait)
        if (not self.user.gameObject) or (self.user.gameObject.roundEnded):
            return

        self.user.gameObject.end_Stage()
        emitToGame(game = self.user.gameObject, arg = ('round_End', {'url':'/gameRoomContent'}), lock = timerLock)
        emitToGame(game = self.user.gameObject, arg = ('client_message', {'msg':'Round ended'}), lock = timerLock)
        return


@socketio.on('handle_chat')
def handleChat(msg):
    #update_chat
    verbose = (False or debugging)
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    if (not user):
        if verbose: print('No user')
        return redirect(url_for('index'))
    game = user.gameObject
    if (not game):
        if verbose: print('No game found when handling chat')
        return

    game.add_Chat_Msg(chatMsg=msg, playerName=user.playerObject.name)

    emitToGame(game=game, arg=('update_chat',{}), lock=timerLock)

@socketio.on('connected')
def client_connect():
    verbose = (False or debugging)
    '''
    I need to identify the user. If the user reloads, the session ID will change.
    A unique user-key is provisided for each new user, and the session ID is updated
    when the user reconnects. The unique ID is stored in a cookie.

    '''
    if verbose: print('Someone connected with the IP: {}'.format(request.remote_addr))
    uniqueID = request.cookies.get('uniqueID')
    if verbose: print('\nUnique ID before update: {}'.format(uniqueID))

    if uniqueID:
        if verbose: print('Unique ID cookie found')
        user = clients.find_User_By_uniqueID(uniqueID)
        if user:
            if verbose: print('User found')
            if request.sid != user.sid:
                user.sid = request.sid
                if verbose: print('Updated the SID')
        else:
            user = clients.add_User(sid=request.sid)
            if verbose: print('User created')
            user.uniqueID = uniqueID
            if verbose: print('Unique ID updated')
    else:
        if verbose: print('Made a new user')
        user = clients.add_User(sid=request.sid)
        if verbose: print('Emitted to server: set_cookie')
        emit(arg=('set_cookie', {'name': 'uniqueID' , 'data': user.uniqueID}), uniqueID = None, lock = timerLock, user= user)

def sendMessageToGame(game, msg):
    for player in game.players:
        emit(arg = ('client_message', {'msg': msg}), uniqueID = None, lock = timerLock, user= player.userObject)

def emitToGame(arg, game, lock):
    for player in game.players:
        emit(arg = arg, uniqueID = None, lock = lock, user = player.userObject)

def emit(arg, uniqueID, lock, user = None):
    '''
    An emit method that requires a lock. Dunno if I need this...
    TODO: Find out if i need the lock.
    '''
    verbose = (False or debugging)

    with lock:
        if verbose: print ('Did an emit')
        if (not user):
            userSID = clients.find_User_By_uniqueID(uniqueID).sid
        else:
            userSID = user.sid
        socketio.emit(*arg, room = userSID)

def userNotComplete(user, verbose = (False or debugging)):
    if verbose:
        print('\nUser name: {}'.format(user.name))
        print('User gameObject pointer {}'.format(user.gameObject))
        print('User playerObject pointer {}\n'.format(user.playerObject))
    if ((not user) or (not user.gameObject) or (not user.playerObject)):
        return True
    else:
        return False

if __name__ == "__main__":
     socketio.run(app, debug = False)
