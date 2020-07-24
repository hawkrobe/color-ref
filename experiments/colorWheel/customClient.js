var UI = require('./drawing.js');

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
  }
 
  $('form').submit(function(){
    var origMsg = $('#chatbox').val();
    var timeElapsed = Date.now() - game.typingStartTime;
    var msg = ['chatMessage', origMsg.replace(/\./g, '~~~'), timeElapsed].join('.');
    if($('#chatbox').val() != '') {
      game.socket.send(msg);
      game.sentTyping = false;
      $('#chatbox').val('');
    }
    // This prevents the form from submitting & disconnecting person
    return false;
  });
 
  game.socket.on('chatMessage', function(data){
    console.log('received cahtMessage');
    console.log(data);
    var source = data.user === game.my_id ? "you" : "partner";    
    var color = data.user === game.my_id ? "#363636" : "#707070";    
    // To bar responses until speaker has uttered at least one message
    game.messageSent = true;
    $('#messages')
      .append($('<li style="padding: 5px 10px; background: ' + color + '">')
    	      .text(source + ": " + data.msg))
      .stop(true,true)
      .animate({
	scrollTop: $("#messages").prop("scrollHeight")
      }, 800);
    console.log('done');
  });

  // game.socket.on('updateScore', function(data) {
  //   console.log('update score');
  //   console.log(data.outcome);
  //   var score = data.outcome == 'target' ? game.bonusAmt : 0;
  //   game.data.score += score;
  //   var bonus_score = (parseFloat(game.data.score) / 100
  // 		       .toFixed(2));
  //   $('#feedback').html('You earned $0.0' + score);
  //   $('#score').empty().append('total bonus: $' + bonus_score);
  //   $('#messages').empty();
  //   $("#context").fadeOut(1000, function() {$(this).empty();});
  //   if(data.outcome == 'target') {
  //     UI.confetti.drop();
  //   }
  // });
    
  game.socket.on('newRoundUpdate', function(data){
    //game.bot = new Bot(game, data);
    game.getPlayer(game.my_id).message = "";
    if(data.active) {
      updateState(game, data);
      UI.reset(game, data);
    }
  });
};

module.exports = customEvents;
