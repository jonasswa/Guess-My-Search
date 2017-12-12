from flask_socketio import SocketIO
from flask import Flask, make_response, request, session
from flask import render_template, session, url_for
from threading import RLock

from TimerSpawner import WaitThread
from ClientStorage import Clients, User

#Init server
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'mys_super_secret_key_I_Guessssss'
socketio = SocketIO(app, async_mode='threading')#,engineio_logger=True)

timerLock = RLock()
clients = Clients()

@app.route('/')
@app.route('/index')
def index():
    content = 'Welcome. This is a test for timing from server. \
                In 10 secouds, the page will be refreshed, \
                and some new content will appear'

    return make_response(render_template('index.html', title = "Welcome", content = content))

@app.route('/newContent')
def newContent():
    return make_response(render_template('new_content.html'))

@socketio.on('connected')
def client_connect():
    verbose = True
    '''
    I need to identify the user. If the user reloads, the session ID will change.
    A unique user-key is provided for each new user, and the session ID is updated
    when the user reconnects. The unique ID is stored in a cookie.
    '''
    if verbose: print ('Connected with ID', str(request.sid))

    if request.cookies.get('uniqueID'):
        uniqueID = request.cookies.get('uniqueID')
        user = clients.find_User_By_uniqueID(uniqueID)
        if user:
            if verbose: print('User exists')
            if user.sid != request.sid:
                user.update_Sid = request.sid
                if verbose: print ('Had to update sid')
        else:
            if verbose: print('User does not exist. But the cookie does')
            user = clients.add_User(request.sid)
            emit(('set_cookie', {'name': 'uniqueID' , 'data': user.uniqueID}), request.sid, timerLock)
            if verbose: print ('Made new user')
    else:
        user = clients.add_User(request.sid)
        emit(('set_cookie', {'name': 'uniqueID' , 'data': user.uniqueID}), user.uniqueID, timerLock)
        if verbose: print ('Made new user')


    testTimer(request.cookies.get('uniqueID'))

def testTimer(uniqueUser):
        timer = WaitThread(10, emit, (('change_content', {'url': '/newContent'}), uniqueUser, timerLock), verbose = True)
        timer.start()

def emit(arg, userUniqueID, lock):
    '''
    An emit method that requires a lock. Dunno if I need this...
    TODO: Find out if i need the lock.
    '''
    with lock:
        userSID = clients.find_User_By_uniqueID(userUniqueID)
        socketio.emit(*arg, room = userSID)

if __name__ == "__main__":
     socketio.run(app)
