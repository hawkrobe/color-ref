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
	  'background' : 'white'
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
  _.forEach(game.currStim, (stim, i) => {
    console.log(stim.color);
    var div = $('<div/>')
	.addClass('pressable-color')
        .addClass('col')
	.attr({'id' : stim.munsellName})
	.css({
          'background' : 'rgb(' + stim.color.join(',') + ')',
          'height' : '250px',
  });
  // for (var rows = 0; rows < 9; rows++) {
  //   for (var columns = 0; columns < 9; columns++) {
  //     $("#color-picker-grid").append(div);
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

  $('#refgame').show();

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

// var colorPicker = function(game) {
//   this.game = game;
//   // TODO: add picker canvas to HTML
//   this.ctx = game.ctx;
//   this.padding = 50;
//   this.centerX = game.viewport.width / 4;
//   this.centerY = game.viewport.height / 2;// - (this.padding/2);
//   this.radius = 110;
// //  this.lightnessTop = 250;
//   this.drawPicker = function() {
//     this.drawDisc();
//     this.drawDiscCursor();
//     // this.drawLightnessRect();
//     // this.drawLightnessCursor();
//   };
//   this.reset = function() {
//     this.discCursorX = this.centerX;
//     this.discCursorY = this.centerY;
// //    this.lightnessCursor = 150;
//     this.hue = 0;
//     this.sat = 0;
//     this.light = 50;
//   };
// };

// colorPicker.prototype.getCurrColor = function() {
//   return [this.hue, this.sat, this.light];
// };

// colorPicker.prototype.discHitTest = function(x, y) {
//   var dx = x - this.centerX;
//   var dy = y - this.centerY;
//   return dx * dx + dy * dy < this.radius * this.radius;
// };

// // colorPicker.prototype.lightnessHitTest = function(x, y) {
// //   var dx = x - this.centerX;
// //   var dy = y - this.lightnessTop;
// //   console.log(dx, dy);
// //   return (Math.abs(dx) < (300 - this.padding * 2)/2 &&
// // 	  0 < dy && dy < this.padding/2);
// // };

// colorPicker.prototype.setDiscCursor = function(x,y) {
//   var dx = x - this.centerX;
//   var dy = y - this.centerY;
//   var R = this.radius - this.radius / 20;
//   if(this.discHitTest(x,y)) {
//     this.discCursorX = x;
//     this.discCursorY = y;
//     this.hue = (angle(dx,dy) + 360) % 360;
//     this.sat = (dx * dx + dy * dy) / this.radius / this.radius * 100;
//   }
// };

// colorPicker.prototype.drawDiscCursor = function() {
//   this.ctx.beginPath();
//   this.ctx.arc(this.discCursorX, this.discCursorY, this.radius/20, 0, 2*Math.PI);
//   this.ctx.stroke();
// };

// // colorPicker.prototype.setLightness = function(x, y) {
// //   if(this.lightnessHitTest(x, y)) {
// //     this.lightnessCursor = x;
// //     this.light = (x - this.padding) / 2;
// //   }
// // };

// // colorPicker.prototype.drawLightnessCursor = function() {
// //   this.ctx.beginPath();
// //   this.ctx.rect(this.lightnessCursor-5, this.lightnessTop - 5,
// // 		10, this.padding/2 + 10);
// //   this.ctx.stroke();
// // };

// colorPicker.prototype.drawDisc = function() {
//   var counterClockwise = false;

//   this.ctx.beginPath();
//   this.ctx.strokeStyle = "#FFFFFF";
//   this.ctx.lineWidth = 5;
//   this.ctx.arc(this.centerX, this.centerY, this.radius + 4, 0, Math.PI * 2);
//   this.ctx.stroke();
//   this.ctx.lineWidth = 1;
  
//   for(var angle=0; angle<=360; angle+=0.5){
//     var startAngle = (angle-2)*Math.PI/180;
//     var endAngle = angle * Math.PI/180;
//     this.ctx.beginPath();
//     this.ctx.moveTo(this.centerX, this.centerY);
//     this.ctx.arc(this.centerX, this.centerY, this.radius,
// 		 startAngle, endAngle, counterClockwise);
//     this.ctx.closePath();
//     var gradient = this.ctx.createRadialGradient(this.centerX,this.centerY,0,
// 						 this.centerX,this.centerY,this.radius);
//     gradient.addColorStop(0,'hsl('+angle+', 0%, 50%)');
//     gradient.addColorStop(1,'hsl('+angle+', 100%, 50%)');
//     this.ctx.fillStyle = gradient;
//     this.ctx.fill();
//   }
// };

module.exports = {
  confetti,
  drawScreen,
  reset
};
