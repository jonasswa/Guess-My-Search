var socket = io.connect('http://' + document.domain + ':' + location.port);


socket.on('connect', function() {
  console.log('Connecting to socket')
  socket.emit('connected');
});

socket.on('disconnect', function() {
  console.log('Disconnecting from socket')
  socket.emit('disconnect');
});

socket.on('set_cookie', function(params) {
  console.log('Setting cookie')
  document.cookie = String(params.name) + "=" + String(params.data);
});

socket.on('change_content', function(params) {
  console.log('Changing content')
  $( "#content" ).load(params.url);
});

function joinRoom(roomName, myName){
  socket.emit('')

}

function triggerThread(){
  console.log('Client triggered trigger_Thread')
  socket.emit('trigger_Thread');
}
