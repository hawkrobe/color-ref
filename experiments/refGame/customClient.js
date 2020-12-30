var UI = require('./UI.js');

// Update client versions of variables with data received from
// server_send_update function in game.core.js
// -- data: packet send by server
function updateState (game, data){
  game.active = data.active;
  game.my_role = data.currStim.roles[game.my_id];
  game.phase = data.currStim.phase;
  game.numTrials = data.currStim.numTrials;

  // For pre- and post-tests, we get trialSeq bundle & shuffle
  if(game.phase != 'refGame') {
    game.trialSeq = _.map(_.shuffle(data.currStim.trialSeq), (trial, i) => {
      return _.extend({}, trial, {trialNum: i});
    });
    game.currStim = game.trialSeq.shift();
  } else {
    game.currStim = data.currStim;
  }

  game.condition = game.currStim.condition;
  game.context = game.currStim.context;
  game.target = game.currStim.target;  
  game.blockNum = game.currStim.blockNum;
  game.trialNum = game.currStim.trialNum;
  game.roundStartTime = Date.now();
  game.messageSent = false;
  game.responseSent = false;
};

var customEvents = function(game) {
  $('.form-group').change({game: game}, UI.dropdownTip);
  $('#surveySubmit').click({game: game}, UI.submit);

  // when you receive a color, highlight it
  game.socket.on('colorReceived', function(data){
    game.receivedColorTime = Date.now();
    game.messageSent = true;
    $('#' + data.id).css({
      'outline-color' : '#FFF', 
      'outline-width' : '8px', 
      'outline-style' : 'solid'
    });
  });

  // at the end of the round, show feedback
  game.socket.on('updateScore', function(data){
    // indicate target
    $('#' + game.target).removeClass('distractor').addClass('target');
    $('#' + game.target + '_targetarrow').addClass('target-arrow').text('target');

    // indicate object that was selected
    const selectedText = game.my_role == 'listener' ? 'You chose: ' : 'Your partner chose: ';
    $('#' + data.outcome).removeClass('distractor').addClass('selected');
    $('#' + data.outcome + '_selectedarrow').addClass('selected-arrow').text(selectedText);

    // write a feedback message in upper-right corner
    const mainMsg = (
      data.outcome != game.target ? "Oops, no bonus this time!" : "Correct! You earned 3 points!"
    );
    $('#feedback').append($('<h3/>').html(mainMsg));

    // increment score
    game.data.score += data.outcome == game.target ? 0.03 : 0;

    // strike out selected text to emphasize error for listener
    if(game.my_role == 'listener' && data.outcome != game.target)
      $('#' + data.outcome).css({'text-decoration': 'line-through'});
  });

  // on new round, reset UI elements for current 'phase' (e.g. pre/post or refGame)
  game.socket.on('newRoundUpdate', function(data){
    game.getPlayer(game.my_id).message = "";
    updateState(game, data);
    UI.reset(game, data);
  });
};

module.exports = customEvents;
