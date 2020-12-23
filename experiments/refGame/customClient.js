var UI = require('./UI.js');

// Update client versions of variables with data received from
// server_send_update function in game.core.js
// -- data: packet send by server
function updateState (game, data){
  console.log('id: ' + game.my_id);
  console.log(data.currStim.roles);
  game.my_role = data.currStim.roles[game.my_id];
  game.condition = data.currStim.condition;
  game.context = data.currStim.context;
  game.target = data.currStim.target;  
  game.active = data.active;
  game.blockNum = data.blockNum;
  game.trialNum = data.trialNum;  
  game.roundStartTime = Date.now();
  game.messageSent = false;
  game.responseSent = false;
};

var customEvents = function(game) {
  // when you receive a color, highlight it
  game.socket.on('colorReceived', function(data){
    game.messageSent = true;
    $('#' + data.id).css({
      'outline-color' : '#FFF', 
      'outline-width' : '8px', 
      'outline-style' : 'solid'
    });
  });

  game.socket.on('updateScore', function(data){
    $('#' + game.target).removeClass('distractor').addClass('target');

    if(data.outcome != game.target & game.my_role == 'listener')
      $('#' + data.outcome).css({'text-decoration': 'line-through'});

    // show arrow above 
    game.data.score += data.outcome == game.target ? 0.02 : 0;
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
