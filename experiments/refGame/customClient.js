var UI = require('./UI.js');

// Update client versions of variables with data received from
// server_send_update function in game.core.js
// -- data: packet send by server
function updateState (game, data){
  game.my_role = data.currStim.roles[game.my_id];
  game.condition = data.currStim.condition;
  game.context = data.currStim.context;
  game.target = data.currStim.target;  
  game.active = data.active;
  game.blockNum = data.blockNum;
  game.trialNum = data.currStim.trialNum;
  game.numTrials = data.currStim.numTrials;
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

  // at the end of the round, show feedback
  game.socket.on('updateScore', function(data){
    // show target
    $('#' + game.target).removeClass('distractor').addClass('target');
    $('#' + game.target + '_targetarrow').addClass('target-arrow').text('target');

    // show object that was selected
    $('#' + data.outcome).removeClass('distractor').addClass('selected');
    $('#' + data.outcome + '_selectedarrow').addClass('selected-arrow').text('selected');

    // write a feedback message
    let mainMsg;
    let subMsg;    
    if(data.outcome != game.target) {
      mainMsg = "Oops, no bonus this time!";
      subMsg = (game.my_role == 'listener' ?
                "You picked <strong>" + data.outcome + "</strong> \
                 but the target was <strong>" + game.target + "</strong>.":
                "Your partner picked <strong>" + data.outcome + "</strong> \
                 instead of <strong>" + game.target + '</strong>.');
    } else {
      mainMsg = "Correct! You earned 2 points!";
      subMsg = (game.my_role == 'listener' ?
                "The target was <strong>" + game.target + "</strong>.":
                "Your partner picked the target.");
    }
    $('#feedback').append($('<h3/>').html(mainMsg));
    $('#feedback').append($('<p/>').html(subMsg));    

    // increment score
    game.data.score += data.outcome == game.target ? 0.02 : 0;

    // strike out selected text to emphasize error for listener
    if(game.my_role == 'listener' && data.outcome != game.target)
      $('#' + data.outcome).css({'text-decoration': 'line-through'});
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
