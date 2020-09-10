var Confetti = require('./src/confetti.js');
var munsell = _.cloneDeep(require('./munsell-gibson.json'));
var confetti = new Confetti(300);

// This gets called when someone selects something in the menu during the 
// exit survey... collects data from drop-down menus and submits using mmturkey
function dropdownTip(data){
  var commands = data.split('::');
  switch(commands[0]) {
  case 'human' :
    $('#humanResult').show();
    globalGame.data = _.extend(globalGame.data, 
                               {'thinksHuman' : commands[1]}); break;
  case 'language' :
    globalGame.data = _.extend(globalGame.data, 
                               {'nativeEnglish' : commands[1]}); break;
  case 'partner' :
    globalGame.data = _.extend(globalGame.data,
                               {'ratePartner' : commands[1]}); break;
  case 'confused' :
    globalGame.data = _.extend(globalGame.data,
                               {'confused' : commands[1]}); break;
  case 'submit' :
    globalGame.data = _.extend(globalGame.data, 
                               {'comments' : $('#comments').val(),
                                'strategy' : $('#strategy').val(),
                                'role' : globalGame.my_role,
                                'totalLength' : Date.now() - globalGame.startTime});
    globalGame.submitted = true;
    console.log("data is...");
    console.log(globalGame.data);
    if(_.size(globalGame.urlParams) >= 4) {
      globalGame.socket.send("exitSurvey." + JSON.stringify(globalGame.data));
      window.opener.turk.submit(globalGame.data, true);
      window.close(); 
    } else {
      console.log("would have submitted the following :")
      console.log(globalGame.data);
    }
    break;
  }
}

function setupListenerHandlers(game) {
  $('div.pressable-text').click(function(event) {
    // Only let listener click once they've heard answer back
    if(game.messageSent) {
      var clickedId = $(this).attr('id');
      game.sendAnswer(clickedId);
      $(this).css({
        'border-color' : '#FFFFFF', 
        'border-width' : '10px', 
        'border-style' : 'solid'
      });
      $('#target').css({
        'border-color' : '#458B00', 
        'border-width' : '10px', 
        'border-style' : 'solid'
      });
    }
  });
}

function setupSpeakerHandlers(game) {
  $('div.pressable-color').click(function(event) {
    // Only let listener click once they've heard answer back
    if(game.messageSent) {
      var clickedId = $(this).attr('id');
      game.sendAnswer(clickedId);
      $(this).css({
        'border-color' : '#FFFFFF', 
        'border-width' : '10px', 
        'border-style' : 'solid'
      });
    }
  });
}

function initStimGrid(game) {
  // Add objects to grid
  _.forEach(game.currStim, (stim, i) => {
    console.log(stim);
    var div = $('<div/>')
        .addClass('pressable-text')
        .addClass('col')
        .attr({'id' : stim.word})
        .text(stim.word)
        .css({
          'background' : 'white',
          'height' : '250px'
        });
    $("#word-grid").append(div);
  });

  // Allow listener to click on things
  game.selections = [];
  if (game.my_role === game.playerRoleNames.role2) {
    console.log('seting up');
    setupListenerHandlers(game);
  }
}

function initColorGrid(game) {
  // Add objects to grid
  _.forEach(munsell, (stim, i) => {
    console.log(stim);
    var div = $('<div/>')
        .addClass('pressable-color')
        .addClass('col')
        .attr({'id' : stim.munsellName})
        .css({
          'background' : 'rgb' + stim.rgb,
          'height' : '250px',
        });
    $("#color-picker-grid").append(div);
  // for (var rows = 0; rows < 9; rows++) {
  //   for (var columns = 0; columns < 9; columns++) {

  //   };
  // };
  // $(".grid").width(960/9);
  // $(".grid").height(960/9);
  });
  
  // Allow listener to click on things
  game.selections = [];
  if (game.my_role === game.playerRoleNames.role1) {
    setupSpeakerHandlers(game);
  }
}

function drawScreen (game) {
  var player = game.getPlayer(game.my_id);
  if (player.message) {
    $('#waiting').html(this.player.message);
  } else {
    $('#waiting').html('');
    confetti.reset();
    initColorGrid(game);
    initStimGrid(game);
    
  }
};

function reset (game, data) {
  $('#scoreupdate').html(" ");
  if(game.roundNum + 1 > game.numRounds) {
    $('#roundnumber').empty();
    $('#instructs').empty()
      .append("Round\n" + (game.roundNum + 1) + "/" + game.numRounds);
  } else {
    $('#feedback').empty();
    $('#roundnumber').empty()
      .append("Round\n" + (game.roundNum + 1) + "/" + game.numRounds);
  }

  $('#main-div').show();

  // reset labels
  // Update w/ role (can only move stuff if agent)
  $('#role').empty().append("You are the " + game.my_role + '.');
  $('#instructs').empty();
  if(game.my_role === game.playerRoleNames.role1) {
    $('#instructs')
      .append("<p>Fill in the question so your partner</p> " +
              "<p>can help you complete the highlighted combo!</p>");
  } else if(game.my_role === game.playerRoleNames.role2) {
    $('#instructs')
      .append("<p>After your partner types their question, </p>" 
              + "<p>pick a color!</p>");
  }
  drawScreen(game);
}


module.exports = {
  confetti,
  drawScreen,
  reset
};
