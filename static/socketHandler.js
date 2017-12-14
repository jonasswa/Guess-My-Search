var socket = io.connect('http://' + document.domain + ':' + location.port);


socket.on('connect', function() {
  console.log('Connecting to socket');
  socket.emit('connected');
});

socket.on('disconnect', function() {
  console.log('Disconnecting from socket');
  socket.emit('disconnect');
});

socket.on('set_cookie', function(params) {
  console.log('Setting cookie');
  document.cookie = String(params.name) + "=" + String(params.data);
});

socket.on('change_content', function(params) {
  console.log('Changing content');
  $( "#content" ).load(params.url);
});


socket.on('client_message', function(params) {
  console.log('Getting client message from server');
  var msg = params.msg;
  if (msg){
    notyf.confirm(msg);
  }
  else{
    console.log('But there was no message');
  }
});

socket.on('client_warning', function(params) {
  console.log('Getting client message from server');
  var msg = params.msg;
  if (msg){
    notyf.alert(msg);
  }
  else{
    console.log('But there was no message');
  }
});


socket.on('refresh_Player_List', function(){
  console.log('Server told client to refresh player list');
  refreshPlayerList();

});

socket.on('update_chat', function(){
  console.log('Chatmsg made by user. Refreshing chat')
  $("#loadChat").load("/chatContent");
});

function leaveGame(){
  console.log('Leaving the game');
  window.location.replace('/leave_Game');
}
function refreshPlayerList(){
  console.log('Refreshed the player list')
  $( "#playerList" ).load('/playerList');
}

function sendChat(){
  console.log('Sending chat...')
  var msg = document.getElementById("chatText").value
  socket.emit('handle_chat', msg)
  document.getElementById("chatText").value = '';
}

function triggerThread(){
  console.log('Client triggered trigger_Thread')
  socket.emit('trigger_Thread');
}

var toggled = false;
function toggleReady(){
  //Switch
  toggled = !toggled;
  console.log('Toggled. Value of the checkbox is: ' + String(toggled));

  socket.emit('toggle_ready', toggled)
}
