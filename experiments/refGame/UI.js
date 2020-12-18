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
  $('div.pressable-text').click(function(event) {
    // Only let listener click a word once they've heard answer back
    if(game.messageSent & !game.responseSent) {
      var clickedId = $(this).attr('id');
      game.responseSent = true;
      game.socket.send('sendResponse.' + clickedId);
      $(this).addClass('bg-dark');
      $('#' + game.target).addClass('bg-warning');
    }
  });
}

function setupSpeakerHandlers(game) {
  $('div.pressable-color').click(function(event) {
    if(!game.messageSent) {
      // Only let listener click once they've heard answer back
      var clickedId = $(this).attr('id');
      console.log($(this));
      game.messageSent = true;
      game.socket.send('sendColor.' + clickedId);
      $(this).css({
        'border-color' : '#FFFFFF',
        'border-width' : '2px',
        'border-style' : 'solid'
      });
    }
  });
}

function initStimGrid(game) {
  // Add objects to grid
  _.forEach(_.shuffle(game.context), (word, i) => {
    var div = $('<div/>')
        .addClass('col h2 pressable-text border rounded-pill')
        .append($('<div/>').addClass('box text-center').text(word))
        .attr({'id' : word});

    // Display target to speaker
    if(word == game.target && game.my_role == game.playerRoleNames.role1) {
      div.addClass('border border-dark');
      div.addClass('font-weight-bold');
      div.addClass('bg-light');
    } else {
      div.addClass('border border-light');
      div.addClass('bg-white');
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
  // bootstrap only allows subdivisions of 12 columns, so we nest rows to get even grid (i.e. 8 = 2 sets of 4=3/12).
  let blockDiv = $('<div/>').addClass('row');
  _.forEach(munsell, (stim, i) => {
    var colorDiv = $('<div/>')
        .addClass('pressable-color')
        .addClass('col-3')
        .css({
          'background' : 'rgb' + stim.rgb,
          'height' : '50px',
        })
        .attr({'id' : stim.munsell});
    console.log(stim);
    blockDiv.append(colorDiv);

    // append and reset at end of block of 4 colors
    if(i % 4 == 3) {
      $("#color-picker-grid").append($('<div/>').addClass('col-6').append(blockDiv));
      blockDiv = $('<div/>').addClass('row');
    }
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
  $('#scoreupdate').html(" ");
  $("#color-picker-grid").html("");
  $("#word-grid").html("");
  if(game.trialNum + 1 > game.numTrials) {
    $('#roundnumber').empty();
    $('#instructs').empty()
      .append("Round\n" + (game.trialNum + 1) + "/" + game.numTrials);
  } else {
    $('#feedback').empty();
    $('#roundnumber').empty()
      .append("Round\n" + (game.trialNum + 1) + "/" + game.numTrials);
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
