from flask_socketio import SocketIO
from flask import Flask, make_response, request, session
from flask import render_template, session, url_for
from threading import RLock

from TimerSpawner import WaitThread
from ClientStorage import Clients, User

#Init server
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'lskwod=91230?=)ASD?=)("")@'
socketio = SocketIO(app, async_mode='threading')#,engineio_logger=True)

timerLock = RLock()
clients = Clients()

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def index():
    error = request.args.get('error')
    if request.method == 'POST':
        if request.form.get('GameID'):
            gameName = request.form.get('GameID')
            name = request.form.get('Name')
            #Join existing game
            response = redirect(url_for('gameRoom'))
            response.set_cookie('name', name)
            response.set_cookie('gameID', gameID)
            return response

    error = None
    return make_response(render_template('makeGame.html', title = "Welcome", error = error))

@socketio.on('connected')
def client_connect():
    verbose = False
    '''
    I need to identify the user. If the user reloads, the session ID will change.
    A unique user-key is provided for each new user, and the session ID is updated
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
                print('Updated the SID')
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

def emit(arg, uniqueID, lock):
    '''
    An emit method that requires a lock. Dunno if I need this...
    TODO: Find out if i need the lock.
    '''
    with lock:
        print ('Did an emit')
        userSID = clients.find_User_By_uniqueID(uniqueID).sid
        socketio.emit(*arg, room = userSID)

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
#     uniqueID = requ1000est.cookies.get('uniqueID')
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
