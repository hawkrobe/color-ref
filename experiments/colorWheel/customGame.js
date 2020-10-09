var _ = require('lodash');
var fs    = require('fs');
var assert = require('assert');
var utils  = require(__base + 'src/sharedUtils.js');
var ServerGame = require(__base + 'src/game.js')['ServerGame'];

class ServerRefGame extends ServerGame {
  constructor(config) {
    super(config);
    this.contexts = {
      'concrete' : _.clone(_.sample(require('../../data/contexts/concrete-contexts.json'))),
      'abstract' : _.clone(_.sample(require('../../data/contexts/abstract-contexts.json')))
    };
    this.numBlocks = 6;
    this.numTrialsInBlock = 8;
    this.numTrials = this.numBlocks * this.numTrialsInBlock;
    this.firstRole = _.sample(['speaker', 'listener']);
    this.trialList = this.makeTrialList();
  }

  customEvents (socket) {}
  
  // *
  // * TrialList creation
  // *

  getRandomizedConditions() {
    var numEach = this.numTrialsInBlock / 2;
    var conditions = [].concat(utils.fillArray("concrete", numEach),
                               utils.fillArray("abstract", numEach));
    return _.shuffle(conditions);
  };

  makeTrialList () {
    var trialList = [];
    _.forEach(_.range(this.numBlocks), blockNum => {
      trialList.push(...this.sampleBlock(blockNum));
    });
    return(trialList);
  };

  sampleBlock (blockNum) {
    var conditionList = this.getRandomizedConditions();
    var tmp_concrete = _.shuffle(_.clone(this.contexts['concrete']['words']));
    var tmp_abstract = _.shuffle(_.clone(this.contexts['abstract']['words']));
    return _.map(conditionList, (conditionName, trialInBlock) => {
      var roleNames = (this.playersThreshold == 1 ? [this.firstRole] : 
                       _.values(this.playerRoleNames));
      return {
        condition: conditionName,
        context: this.contexts[conditionName]['words'],
        context_id: conditionName + '_' + this.contexts[conditionName]['id'],
        target: (conditionName == 'concrete' ?
                 tmp_concrete.pop() :
                 tmp_abstract.pop()),
        blockNum : blockNum,
        trialNum : blockNum * 8 + trialInBlock,
        roles: _.zipObject(_.map(this.players, p => p.id), roleNames)
      };
    });
  }
  
  onMessage (client, message) {
    //Cut the message up into sub components
    var message_parts = message.split('.');

    //The first is always the type of message
    var message_type = message_parts[0];

    //Extract important variables
    var gc = client.game;
    var id = gc.id;
    var all = gc.activePlayers();
    var target = gc.getPlayer(client.userid);
    var others = gc.getOthers(client.userid);
    switch(message_type) {

  
    case 'sendColor' :
      console.log('sending color');
      console.log(message_parts);
      if(client.game.playerCount == gc.playersThreshold && !gc.paused) {
        _.map(all, p => p.player.instance.emit( 'colorReceived', {
          user: client.userid, id: message_parts[1]
        }));
      }
      break;
      
    case 'sendResponse' :
      _.map(all, p => p.player.instance.emit('updateScore', {
        outcome: message_parts[1]
      }));
      setTimeout(function() {
        _.map(all, function(p){
          p.player.instance.emit( 'newRoundUpdate', {user: client.userid} );
        });
        gc.newRound();
      }, 3000);
        
      break; 

    case 'exitSurvey' :
      console.log(message_parts.slice(1));
      break;
      
    case 'h' : // Receive message when browser focus shifts
      //target.visible = message_parts[1];
      break;
    }
  };

  /*
    Associates events in onMessage with callback returning json to be saved
    {
    <eventName>: (client, message_parts) => {<datajson>}
    }
    Note: If no function provided for an event, no data will be written
  */
  dataOutput () {
    // function commonOutput (client, message_data) {
    //   //var target = client.game.currStim.target;
    //   //var distractor = target == 'g1' ? 'g0' : 'g1';
    //   return {
    //  iterationName: client.game.iterationName,
    //  gameid: client.game.id,
    //  time: Date.now(),
    //  workerId: client.workerid,
    //  assignmentId: client.assignmentid,
    //  trialNum: client.game.roundNum,
    //  trialType: client.game.currStim.currGoalType,
    //  // targetGoalSet: client.game.currStim.goalSets[target],
    //  // distractorGoalSet: client.game.currStim.goalSets[distractor],
    //  firstRole: client.game.firstRole
    //   };
    // };
    
    // var revealOutput = function(client, message_data) {
    //   var selections = message_data.slice(3);
    //   var allObjs = client.game.currStim.hiddenCards;
    //   return _.extend(
    //  commonOutput(client, message_data), {
    //    sender: message_data[1],
    //    timeFromMessage: message_data[2],
    //    revealedObjs : selections,
    //    numRevealed : selections.length,
    //    fullContext: JSON.stringify(_.map(allObjs, v => {
    //      return _.omit(v, ['rank', 'suit', 'url']);
    //    }))
    //  });
    // };
    

    // var exitSurveyOutput = function(client, message_data) {
    //   var subjInfo = JSON.parse(message_data.slice(1));
    //   return _.extend(
    //  _.omit(commonOutput(client, message_data),
    //         ['targetGoalSet', 'distractorGoalSet', 'trialType', 'trialNum']),
    //  subjInfo);
    // };
    

    // var messageOutput = function(client, message_data) {
    //   return _.extend(
    //  commonOutput(client, message_data), {
    //    cardAskedAbout: message_data[1],
    //    sender: message_data[4],
    //    timeFromRoundStart: message_data[3]
    //  }
    //   );
    // };

    return {
      // 'chatMessage' : emptyF,
      // 'reveal' : emptyF,
      // 'exitSurvey' : emptyF
    };
  }
}

class GameMap {
  constructor(trialType) {
    this.labels = [
      'A1', 'A2', 'A3', 'A4',
      'B1', 'B2', 'B3', 'B4',
      'C1', 'C2', 'C3', 'C4',
      'D1', 'D2', 'D3', 'D4'
    ];
    this.trialType = trialType;

    const origMap = [
      ['g' ,'g', 'g', 'g'],
      ['g', 'g', 'g', 'g'],
      ['r', 'r', 'r', 'r'],
      ['r', 'r', 'r', 'r']
    ];

    // Sample 1 of the 4 possible transformations
    const transformation = _.sample([
      x => x,
      x => this.rotate(x),
      x => this.reflect(this.rotate(x)),
      x => this.rotate(this.reflect(this.rotate(x)))
    ]);
    this.initRevealed = this.sampleInitRevealed(transformation);
    this.grid = this.matrixToDict(transformation(origMap));
    console.log(this.initRevealed);
    console.log(this.grid);
  }
  
  sampleInitRevealed (transformation) {
    const grid = (this.trialType == 'catch' ? this.sampleInitRevealedCatch() :
                  this.trialType == 'pragmatic' ? this.sampleInitRevealedPragmatic() :
                  console.error('unknown trialType' + this.trialType));
    const dict = this.matrixToDict(transformation(grid));
    return _.filter(_.keys(dict), key => dict[key] === 'x');
  }

  matrixToDict (matrix) {
    return _.zipObject(this.labels, _.flatten(matrix));
  }
  
  // This allows 8 possible initial states
  sampleInitRevealedCatch () {
    const initRevealed = [
      ['x' ,'x', 'x', 'o'],
      ['o', 'o', 'o', 'o'],
      ['o', 'o', 'o', 'o'],
      ['o', 'o', 'o', 'o']
    ];
    return Math.random() < .5 ? initRevealed : this.reflect(initRevealed);
  }

  // This allows 8 possible initial states
  sampleInitRevealedPragmatic () {
    const initRevealed = [
      ['x' ,'x', 'o', 'o'],
      ['x', 'o', 'o', 'o'],
      ['o', 'o', 'o', 'o'],
      ['o', 'o', 'o', 'o']
    ];
    return Math.random() < .5 ? initRevealed : this.reflect(initRevealed);
  }
  
  rotate (grid) {
    return _.zip(...grid);
  }

  reflect (grid) {
    return _.map(grid, row => _.reverse(row.slice()));
  }
}

module.exports = ServerRefGame;
