const player = require('./player.js');
const io = require('socket.io-client');
const _ = require('lodash');

class Game {
  constructor(config){
    this.roundNum = -1;

    this.email = config.email;
    this.projectName = config.projectName;
    this.experimentName = config.experimentName;
    this.iterationName = config.iterationName;
    this.anonymizeCSV = config.anonymizeCSV;
    this.bonusAmt = config.bonusAmt;
    this.dataStore = config.dataStore;
    this.playersThreshold = config.playersThreshold;
    this.playerRoleNames = config.playerRoleNames;
    this.numHorizontalCells = config.numHorizontalCells;
    this.numVerticalCells = config.numVerticalCells;
    this.cellDimensions = config.cellDimensions;
    this.cellPadding = config.cellPadding;
    this.world = {
      height: this.cellDimensions.height * this.numVerticalCells,
      width: this.cellDimensions.width * this.numHorizontalCells
    },
    this.delay = config.delay;
  }

  // Returns player object corresponding to id
  getPlayer (id) {
    return _.find(this.players, {id : id})['player'];
  };

  // Returns all players that aren't the given id
  getOthers (id) {
    var otherPlayersList = _.filter(this.players, e => e.id != id);
    var noEmptiesList = _.map(otherPlayersList, p => p.player ? p : null);
    return _.without(noEmptiesList, null);
  };

  // Returns array of all active players
  activePlayers () {
    return _.without(_.map(this.players, p => p.player ? p : null), null);
  };
};

// ServerGame is copy of game with more specific server-side functions
// Takes a more specific config as well as custom functions to construct
// trial list and advance to next round
class ServerGame extends Game {
  constructor(config) {
    super(config);
    this.active = false;
    this.streams = {};    
    this.id = config.id; 
    this.expPath = config.expPath;
    this.playerCount = config.playerCount;
    this.players = [{
      id: config.initPlayer.userid,
      instance: config.initPlayer,
      player: new player(this, config.initPlayer)
    }];
  }

  // Bundle up server-side info to update client
  takeSnapshot () {
    var playerPacket = _.map(this.players, p => {return {id: p.id, player: null};});
    var state = {
      active : this.active,
      roundNum : this.roundNum,
      currStim: this.currStim,
      objects: this.objects
    };

    _.extend(state, {players: playerPacket});

    return state;
  };

  start (stims) {
    this.active = true;
    this.contexts = stims;
    this.trialList = this.makeTrialList();
    this.numRounds = this.trialList.length;
    this.newRound();
  }

  end () {
    setTimeout(() => {
      _.forEach(this.activePlayers(), p => {
	try {
	  p.player.instance.emit('showExitSurvey', {});
	} catch(err) {
	  console.log('player did not exist to disconnect');
	}
      });
    }, this.delay);
  }
  
  // This is called on the server side to trigger new round
  newRound (delay) {
    if(this.roundNum == this.trialList.length - 1) {
      this.end();
    } else {
      // Otherwise, get the preset list of tangrams for the new round
      this.roundNum += 1;
      this.currStim = this.trialList[this.roundNum];

      // set active to false on post-test so people can drop out without disconnecting other person
      this.active = this.currStim.phase != 'post';      
      var state = this.takeSnapshot();
      setTimeout(() => {
	_.forEach(this.activePlayers(), p => {
	  p.player.instance.emit( 'newRoundUpdate', state);
	});
      }, delay);
    }
  };
}

function getURLParams () {
  var match,
      pl     = /\+/g,  // Regex for replacing addition symbol with a space
      search = /([^&=]+)=?([^&]*)/g,
      decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
      query  = location.search.substring(1);

  var urlParams = {};
  while ((match = search.exec(query))) {
    urlParams[decode(match[1])] = decode(match[2]);
  }
  return urlParams;
};

// ServerGame is copy of game with more specific client-side functions
class ClientGame extends Game {
  constructor (config, customEvents) {
    super(config);
    this.submitted = false;
    this.urlParams = getURLParams();
    this.socket = io({reconnection: false, query: this.urlParams});    
    this.customEvents = customEvents;
    this.startTime = Date.now();

    this.data = {
      score: 0
    };
    
    this.players = [{
      id: null,
      instance: null,
      player: new player(this)
    }];
  }

  listen () {
    this.socket.on('connect', function() {
      console.log('connected... waiting for server info');
    });

    this.socket.on('joinGame', function(data) {
      this.my_id = data.id;
      this.players[0].id = data.id;
      this.data.gameID = data.id;
    }.bind(this));
    
    this.socket.on('addPlayer', function(data) {
      this.players.push({id: data.id, player: new player(this)});
    }.bind(this));
    
    this.socket.on('showExitSurvey', function(data) {
      this.showExitSurvey();
    }.bind(this));

    this.customEvents(this);
  }

  showExitSurvey () {
    console.log(this)
    clearTimeout(this.advanceTimeout);
    var email = this.email ? this.email : '';
    var failMsg = [
      '<h3>Oops! It looks like your partner lost their connection!</h3>',
      '<p> Completing this survey will submit your HIT so you will still receive full ',
      'compensation.</p> <p>If you experience any problems, please email us (',
      email, ')</p>'
    ].join('');
    var successMsg = [
      "<h3>Thanks for participating in our experiment!</h3>",
      "<p>Before you submit your HIT, we'd like to ask you just a couple more questions.</p>"
    ].join('');

    if(this.phase == 'post') { 
      $('#exit_survey').prepend(successMsg);    
    } else {
      $('#exit_survey').prepend(failMsg); 
    }
    $('#waiting').hide();
    $('#main-div').hide();
    $('#pre-post-div').hide();     
    $('#exit_survey').show();
  } 
}

module.exports = {ClientGame, ServerGame};
