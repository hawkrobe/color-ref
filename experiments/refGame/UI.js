var Confetti = require('./src/confetti.js');
var munsell = _.cloneDeep(require('./munsell-gibson-V1-sorting.json'));
var confetti = new Confetti(300);

// This gets called when someone selects something in the menu during the
// exit survey... collects data from drop-down menus and submits using mmturkey

function setupListenerHandlers(game) {
  $('.pressable-text').click(function(event) {
    // Only let listener click a word once they've heard answer back
    if(game.messageSent & !game.responseSent) {
      game.responseSent = true;
      game.socket.emit('saveData', clickPacket(game, $(this).attr('id')));
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
      if(game.phase == 'refGame') {
        game.socket.send('sendColor.' + $(this).attr('id')); 
        game.socket.emit('saveData', colorPacket(game, $(this).attr('id')));
      } else
        advanceTestTrial(game, $(this).attr('id'));
    }
  });
}

function clickPacket(game, clickedId) {
  return _.extend({}, game.urlParams, {
    "dataType" : "clickedWord",
    playerId: game.my_id,
    "rt":  Date.now() - game.receivedColorTime,
    "target": game.currStim.target,
    "trialNum": game.currStim.trialNum,
    "blockNum" : game.currStim.blockNum,
    "phase" : game.currStim.phase,
    "selected_word": clickedId,
    "context_id" : game.currStim.context_id,
    "context" : game.currStim.context,    
    "correct" : game.currStim.target == clickedId
  });
}
  
function colorPacket (game, clickedId) {
  var rgbArray = munsell[_.toInteger(clickedId)].rgb.slice(1,-1).split(', ');
  return _.extend({}, game.urlParams, {
    dataType: "sentColor",
    playerId: game.my_id,
    "rt":  Date.now() - game.roundStartTime,
    "target": game.currStim.target,
    "trialNum": game.currStim.trialNum,
    "blockNum" : game.currStim.blockNum,
    "phase": game.currStim.phase,
    "condition": game.currStim.condition,
    "set": game.currStim.set,
    "context" : game.currStim.context, 
    "context_id" : game.currStim.context_id,
    "button_pressed": clickedId,
    "response_r": _.toInteger(rgbArray[0]),
    "response_g": _.toInteger(rgbArray[1]),
    "response_b": _.toInteger(rgbArray[2]),
    "response_munsell": munsell[_.toInteger(clickedId)].munsell
  });
}

function advanceTestTrial(game, clickedId) {
  game.socket.emit('saveData', colorPacket(game, clickedId));
  
  // highlight clicked object
  $('#' + clickedId).css({
    'outline-color' : '#FFF', 
    'outline-width' : '8px', 
    'outline-style' : 'solid'
  });

  // if we're at end of pre-test, tell the server;
  // otherwise, move to next trial
  game.advanceTimeout = setTimeout(function(){
    if(game.trialSeq.length == 0 & game.phase == 'pre') {
      game.socket.send('finishedPretest');
      resetWaitingScreen('Thanks for your responses!<br/>\
                          You are now ready to begin the game.<br/>\
                          Please wait one moment for your partner<br/>\
                          to finish telling us about their personal associations.<br/>\
                          You’ll begin interacting with them in one moment!');
    } else if(game.trialSeq.length == 0 & game.phase == 'post') {
      game.showExitSurvey();
    } else {
      game.currStim = game.trialSeq.shift();
      game.roundStartTime = Date.now();
      resetColorPicker(game);
    }
  }, 750);
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

function resetWaitingScreen(text) {
  $('#pre-post-div').hide();
  $('#main-div').hide();
  $('#waiting').html(text);
};

function resetRefGame (game, data) {
  // update score counter
  $("#score-counter").text('Total bonus: $' + String(game.data.score.toFixed(2)));

  // note that we need to subtract off the pre- and post trials for this counter...
  $('#trial-counter').empty().append("Trial\n" + (game.trialNum + 1) + "/" + (game.numTrials - 2));

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
  drawScreen(game);
}

// draw everything, and give time to send notification about swapping roles
function reset(game, data) {
  if(data.currStim.phase == 'post') {
    resetWaitingScreen('All done! You earned a performance bonus of $'
		       + String(game.data.score.toFixed(2)) +
                       '. We just have a few last questions for you before you \
                        submit the HIT and get your completion bonus.');
    setTimeout(() => resetColorPicker(game, data), 3000);
  } else if(data.currStim.phase == 'pre') {
    resetColorPicker(game, data);
  } else if(game.trialNum % 8 == 0 && game.trialNum > 1) {
    resetWaitingScreen('Nice work! Time to switch roles. <br/> \
                        For the next few trials, you will be the <strong>'
                       + game.my_role + '</strong>.');
    setTimeout(() => resetRefGame(game, data), 3000);
  } else {
    resetRefGame(game, data);
  }
}

function resetColorPicker (game) {
  // display stimulus
  $('#main-div').hide();
  $('#waiting').html('');
  $("#pre-post-div").html("");
  $('#pre-post-div').show();
  const prompt = $('<h5/>').html("please select the color you personally associate with the word:");
  const word = $('<h2/>').html("<strong>" + game.currStim.target + '</strong>');
  $('#pre-post-div').append(
    $('<div/>').css({'text-align' : 'center', 'margin' : '50px 0px'}).append(prompt).append(word));
  game.messageSent = false;
  initColorGrid(game, $('#pre-post-div'));
  $('#pre-post-div').append(
    $('<h5/>')
      .html(`${game.trialSeq.length + 1} words remaining.`)
      .css({'margin' : '50px 0px'})
  );
};

function dropdownTip(event){
  var game = event.data.game;
  var data = $(this).find('option:selected').val();
  // console.log(data);
  var commands = data.split('::');
  switch(commands[0]) {
  case 'language' :
    game.data = _.extend(game.data, {'nativeEnglish' : commands[1]}); break;
  case 'partner' :
    game.data = _.extend(game.data, {'ratePartner' : commands[1]}); break;
  case 'human' :
    $('#humanResult').show();
    game.data = _.extend(game.data, {'partnerIsHuman' : commands[1]}); break;
  case 'didCorrectly' :
    game.data = _.extend(game.data, {'didCorrectly' : commands[1]}); break;
  }
}

function submit (event) {
  $('#button_error').show();
  var game = event.data.game;
  game.finished = true;
  game.data = _.extend(_.omit(game.data, 'gameID'), {
    'comments' : $('#comments').val().trim().replace(/\./g, '~~~'),
    'strategy' : $('#strategy').val().trim().replace(/\./g, '~~~'),
    'role' : game.my_role,
    'totalLength' : Date.now() - game.startTime,
    'playerId' : game.my_id,
    'score' : game.data.score + 0.06 * game.roundNum
  });
  console.log(game.data);
  game.submitted = true;
  game.socket.emit("saveData", _.extend({'dataType': 'exitSurvey'}, game.urlParams, game.data));
  if(_.size(game.urlParams) >= 4) {
    window.opener.turk.submit(game.data, true);
    window.close();
  } else {
    console.log("would have submitted the following :")
    console.log(game.data);
  }
}

module.exports = {
  confetti,
  reset,
  submit,
  dropdownTip
};

