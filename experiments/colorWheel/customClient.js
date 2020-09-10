var UI = require('./UI.js');

// Update client versions of variables with data received from
// server_send_update function in game.core.js
// -- data: packet send by server
function updateState (game, data){
  console.log('id: ' + game.my_id);
  console.log(data.currStim.roles);
  game.my_role = data.currStim.roles[game.my_id];
  game.condition = data.currStim.condition;
  game.currStim = data.currStim.stimuli;
  game.active = data.active;
  game.roundNum = data.roundNum;
  game.roundStartTime = Date.now();
};

var customEvents = function(game) {
  game.sendAnswer = function(id) {
    game.socket.send('clickedObj.' + id);
  }; 

  game.socket.on('messageReceived', function(data){
    $('#messages')
  });
    
  game.socket.on('newRoundUpdate', function(data){
    game.getPlayer(game.my_id).message = "";
    if(data.active) {
      updateState(game, data);
      UI.reset(game, data);
    }
  });
};

module.exports = customEvents;
