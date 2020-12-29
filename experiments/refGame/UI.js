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
      if(game.phase == 'refGame')
        game.socket.send('sendColor.' + $(this).attr('id'));
      else
        advanceTestTrial(game, $(this).attr('id'));
    }
  });
}

function advanceTestTrial(game, clickedId) {
  // measure rt
  var end_time = new Date();
  var rt = end_time - game.start_time;

  // send data to store
  var rgbArray = munsell[_.toInteger(clickedId)].rgb.slice(1,-1).split(', ');
  game.socket.emit('data', {
    "rt": rt,
    "target": game.currStim.target,
    "trialNum": game.currStim.trialNum,
    "phase": game.currStim.phase,    
    "condition": game.currStim.condition,
    "set": game.currStim.set,    
    "button_pressed": clickedId,
    "response_r": _.toInteger(rgbArray[0]),
    "response_g": _.toInteger(rgbArray[1]),
    "response_b": _.toInteger(rgbArray[2]),
    "response_munsell": munsell[_.toInteger(clickedId)].munsell
  });

  $('#' + clickedId).css({
    'outline-color' : '#FFF', 
    'outline-width' : '8px', 
    'outline-style' : 'solid'
  });

  // if we're at end of pre-test, tell the server;
  // otherwise, move to next trial
  setTimeout(function(){
    if(game.trialSeq.length == 0) {
      game.socket.send('finishedPretest');
    } else {
      game.currStim = game.trialSeq.pop();
      resetColorPicker(game);
    }
  }, 1500);
}

function initStimGrid(game) {
  // Add objects to grid
  _.forEach(_.shuffle(game.context), (word, i) => {
    var div = $('<div/>')
        .addClass('col h2 border pressable-text rounded-pill') // make it a blob with a border
        .css({'margin' : '0px 20px'}) // Make some space for arrow above & below
        .append($('<div/>').addClass('box text-center').text(word)) // stick a word inside the blob
        .attr({'id' : word}); // add an id to the blow so you can grab it later

    // Display target to speaker
    if(word == game.target && game.my_role == game.playerRoleNames.role1) {
      div.addClass('target font-weight-bold'); // bold the word
      div.append($('<span/>').attr({'id' : word + '_targetarrow'}) // add a 'targetarrow' elemnt
                 .addClass('target-arrow').text('target'));        // annotate as target
      div.append($('<span/>').attr({'id' : word + '_selectedarrow'}));
    } else {
      div.addClass('distractor');
      div.append($('<span/>').attr({'id' : word + '_targetarrow'}));
      div.append($('<span/>').attr({'id' : word + '_selectedarrow'}));
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
function initColorGrid(game, display_element) {
  let blockDiv;
  _.forEach(munsell, (stim, i) => {
    var row = Math.floor(i/11);
    var col = i % 11;

    // append and reset at end of row
    if (col == 0) {
      display_element.append(blockDiv);
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
  if (game.phase == 'pre' || game.phase == 'post' || game.my_role === game.playerRoleNames.role1) {
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
    initColorGrid(game, $('#color-picker-grid'));
    initStimGrid(game);
  }
};

function resetRefGame (game, data) {
  // update score & trial counters
  $("#score-counter").text('Total bonus: $' + String(game.data.score.toFixed(2)));
  $('#trial-counter').empty().append("Trial\n" + (game.trialNum + 1) + "/" + game.numTrials);

  // clear display elements
  $('#pre-post-div').html("");
  $('#pre-post-div').hide();
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

function resetColorPicker (game) {
  // display stimulus
  $('#main-div').hide();
  $('#waiting').html('');
  $("#pre-post-div").html("");
  $('#pre-post-div').show();
  const prompt = $('<h5/>').html("please select the color you most closely associate with the word:")
  const word = $('<h2/>').html("<strong>" + game.currStim.target + '</strong>');
  $('#pre-post-div').append(
    $('<div/>').css({'text-align' : 'center', 'margin' : '50px 0px'}).append(prompt).append(word));
  game.messageSent = false;
  initColorGrid(game, $('#pre-post-div'));
  $('#pre-post-div').append(
    $('<h5/>')
      .html(`${game.trialSeq.length + 1} words remaining before game starts.`)
      .css({'margin' : '50px 0px'})
  );
};

module.exports = {
  confetti,
  drawScreen,
  resetRefGame,
  resetColorPicker
};

