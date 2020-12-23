var Confetti = require('./src/confetti.js');
var munsell = _.cloneDeep(require('./munsell-gibson-V1-sorting.json'));
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
  $('.pressable-text').click(function(event) {
    // Only let listener click a word once they've heard answer back
    if(game.messageSent & !game.responseSent) {
      game.responseSent = true;
      game.socket.send('sendResponse.' + $(this).attr('id'));
    }
  });
}

function setupSpeakerHandlers(game) {
  $('.pressable-color')
    .hover(
      function() {if(!game.messageSent) $(this).addClass("btn-hover"); },
      function() { $(this).removeClass("btn-hover"); }
    );


  $('.pressable-color').click(function(event) {
    if(!game.messageSent) {
      // Only let listener click once they've heard answer back
      $(this).removeClass("btn-hover");
      game.messageSent = true;
      game.socket.send('sendColor.' + $(this).attr('id'));
    }
  });
}

function initStimGrid(game) {
  // Add objects to grid
  _.forEach(_.shuffle(game.context), (word, i) => {
    var div = $('<div/>')
        .addClass('col h2 border pressable-text rounded-pill')
        .css({'margin' : '0px 20px'})
        .append($('<div/>').addClass('box text-center').text(word))
        .attr({'id' : word});

    // Display target to speaker
    if(word == game.target && game.my_role == game.playerRoleNames.role1) {
      div.addClass('target font-weight-bold');
    } else {
      div.addClass('distractor');
    }
    $("#word-grid").append(div);
  });

  // Allow listener to click on things
  game.selections = [];
  if (game.my_role === game.playerRoleNames.role2) {
    setupListenerHandlers(game);
  }
}

// Add objects to grid
function initColorGrid(game) {
  let blockDiv;// = $('<div/>').addClass('btn-group');
  _.forEach(munsell, (stim, i) => {
    var row = Math.floor(i/11);
    var col = i % 11;

    // append and reset at end of row
    if (col == 0) {
      $("#color-picker-grid").append(blockDiv);
      blockDiv = $('<div/>').addClass('btn-group').css({'margin-bottom':'8px'});

      // offset odd rows to make 'brick' wall
      if(row % 2 == 0) 
        blockDiv.css({'margin-left': '40px'});
    }
    blockDiv.append(
      $('<div/>')
        .addClass('pressable-color')
        .css({
          'display' : 'inline-block',
          'background' : 'rgb' + stim.rgb,
          'height' : '50px',
          'width' : '80px',
          'margin' : '0px 4px'
        })
        .attr({
          'id' : stim.id,
          'data-choice' : stim.id
        })
    );
  });

  // Allow listener to click on things
  game.selections = [];
  if (game.my_role === game.playerRoleNames.role1) {
    console.log('setup handler');
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
  // update score & trial counters
  $("#score-counter").text('Total bonus: $' + String(game.data.score.toFixed(2)));
  $('#trial-counter').empty().append("Trial\n" + (game.trialNum + 1) + "/" + game.numTrials);

  // clear display elements
  $("#color-picker-grid").html("");
  $("#word-grid").html("");
  $('#feedback').empty();
  $('#main-div').show();

  // reset role header/instruct (allows for switching roles)
  $('#role').empty().append("You are the " + game.my_role + '.');
  const instruct = game.my_role === game.playerRoleNames.role1 ? (
    "<p>Click on a color that will allow your partner to pick the highlighted word!</p>"
  ) : (
    "<p>After your partner sends you a color, click on the word \
        you think they're trying to communicate.</p>"
  );
  $('#instructs').empty().append(instruct);

  // draw everything
  drawScreen(game);
}


module.exports = {
  confetti,
  drawScreen,
  reset
};
