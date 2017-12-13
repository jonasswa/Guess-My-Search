from flask_socketio import SocketIO
from flask import Flask, make_response, request, session
from flask import render_template, session, url_for, redirect
from threading import RLock

from TimerSpawner import WaitThread
from ClientStorage import Clients, User

from gameObjects import Game, GameContainter, Player

#Init server
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'lskwod=91230?=)ASD?=)("")@'
socketio = SocketIO(app, async_mode='threading')#,engineio_logger=True)

timerLock = RLock()
clients = Clients()

games = GameContainter()


@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def index():
    verbose = False
    error = request.args.get('error')
    return make_response(render_template('makeGame.html', title = "Welcome", error = error))

@app.route('/gameRoom', methods = ['POST', 'GET'])
def gameRoom():
    global games
    verbose = True
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

            print('In server:gameRoom() Searching for game: {}'.format(data['gameName']))
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


    else:
        print('USER IN GAME')
        #emit(('client_message', {'msg': 'You are in a game'}), user.uniqueID, timerLock)
    print(games)
    print(user.gameObject.gameName)
    error = None
    return make_response(render_template('gameRoom.html', title = "Game Room", gameName = user.gameObject.gameName, error = error))



@app.route('/gameRoomContent')
def gameRoomContent():
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)

    if userNotComplete(user, verbose = False):
         return redirect(url_for('index') + '?error=User not in game')

    if (not user.gameObject.gameStarted):
        playerList = user.gameObject.getPlayerNames()
        return render_template('lobbyContent.html', playerList = playerList)

@app.route('/playerList')
def playerList():
    uniqueID = request.cookies.get('uniqueID')
    user = clients.find_User_By_uniqueID(uniqueID)
    verbose = False
    if userNotComplete(user, verbose = False):
        return redirect(url_for('index') + '?error=User not in game')

    playerList = user.gameObject.getPlayerNames()
    if verbose: print('Got {} players'.format(len(playerList)))
    return render_template('playerList.html', playerList = playerList)


@socketio.on('connected')
def client_connect():
    verbose = False
    '''
    I need to identify the user. If the user reloads, the session ID will change.
    A unique user-key is provisided for each new user, and the session ID is updated
    when the user reconnects. The unique ID is stored in a cookie.

    '''
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
        emit(('set_cookie', {'name': 'uniqueID' , 'data': user.uniqueID}), user.uniqueID, timerLock)

def sendMessageToGame(game, msg):
    for player in game.players:
        emit(arg = ('client_message', {'msg': msg}), uniqueID = None, lock = timerLock, user= player.userObject)

def emit(arg, uniqueID, lock, user = None):
    '''
    An emit method that requires a lock. Dunno if I need this...
    TODO: Find out if i need the lock.
    '''
    with lock:
        print ('Did an emit')
        if (not user):
            userSID = clients.find_User_By_uniqueID(uniqueID).sid
        else:
            userSID = user.sid
        socketio.emit(*arg, room = userSID)

def userNotComplete(user, verbose = False):
    if verbose:
        print('\nUser name: {}'.format(user.name))
        print('User gameObject pointer {}'.format(user.gameObject))
        print('User playerObject pointer {}\n'.format(user.playerObject))
    if ((not user) or (not user.gameObject) or (not user.playerObject)):
        return True
    else:
        return False

#Stored for future
# @app.route('/test')
# def test():
#     content = 'Welcome. This is a test for timing from server. \
#                 In 10 secouds, the page will be refreshed, \
#                 and some new contenuserSIDt will appear'
#
#     return make_response(render_template('index.html', title = "Welcome", content = content))
#
# @socketio.on('trigger_Thread')
# def trigger_Thread():
#
#     uniqueID = request.cookies.get('uniqueID')
#     print('The unique ID for the trigger: {}'.format(uniqueID))
#     print(clients)
#
#     if (not uniqueID):
#         print('uniqueID NOT FOUND in thread_trigger')
#         return
#
#     testTimer(uniqueID)
#
# def testTimer(uniqueID):
#
#     user = clients.find_User_By_uniqueID(uniqueID)
#     timer = WaitThread(2, emit, (('change_content', {'url': '/newContent'}), uniqueID, timerLock), user.update_Thread_Number, verbose = True)
#     try:
#         timer.start()
#     except:
#         print('Thread does not exist')

if __name__ == "__main__":
     socketio.run(app)
