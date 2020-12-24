var _ = require('lodash');
var fs    = require('fs');
var assert = require('assert');
var utils  = require(__base + 'src/sharedUtils.js');
var ServerGame = require(__base + 'src/game.js')['ServerGame'];

class ServerRefGame extends ServerGame {
  constructor(config) {
    super(config);
    const concretes = _.clone(_.sampleSize(require('../../data/contexts/divergence-rejection-sampling/concrete-contexts.json'), 2));
    const abstracts = _.clone(_.sampleSize(require('../../data/contexts/divergence-rejection-sampling/abstract-contexts.json'), 2));
    console.log(concretes);
    this.contexts = {
      'concrete' : concretes[0],
      'abstract' : abstracts[0],
    };
    this.controls = {
      'concrete' : concretes[1],
      'abstract' : abstracts[1]
    };
    this.numBlocks = 6;
    this.numTrialsInBlock = 8;
    this.ready = false;
    this.numTrials = this.numBlocks * this.numTrialsInBlock;
    this.firstRole = _.sample(['speaker', 'listener']);
    this.trialList = this.makeTrialList();
  }

  customEvents (socket) {
    
  }

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
    trialList.push(this.makeTestSequence('pre'));
    _.forEach(_.range(this.numBlocks), blockNum => {
      trialList.push(...this.sampleBlock(blockNum));
    });
    trialList.push(this.makeTestSequence('post'));
    return(trialList);
  };

  makeTestSequence (phase){
    const trialSeq = [];
    _.forEach(['concrete', 'abstract'], condition => {
      _.forEach(['test', 'control'], set => {
        const words = (set == 'test' ? this.contexts[condition]['words'] :
                       this.controls[condition]['words']);
        _.forEach(words, word => {
          trialSeq.push({phase: phase, target: word, condition: condition,
                         set: set});
        });
      });
    });
    return {
      phase: phase,
      numTrials: this.numTrials,
      roles: _.zipObject(_.map(this.players, p => p.id), ['picker', 'picker']),
      trialSeq : _.map(_.shuffle(trialSeq), (trial, i) => {
        return _.extend({}, trial, {trialNum: i});
      })
    };
  }
  
  sampleBlock (blockNum) {
    var conditionList = this.getRandomizedConditions();
    var tmp_concrete = _.shuffle(_.clone(this.contexts['concrete']['words']));
    var tmp_abstract = _.shuffle(_.clone(this.contexts['abstract']['words']));
    return _.map(conditionList, (conditionName, trialInBlock) => {
      var roleNames = (this.playersThreshold == 1 ? [this.firstRole] :
                       _.values(this.playerRoleNames));
      return {
        condition: conditionName,
        phase: 'refGame',
        context: this.contexts[conditionName]['words'],
        context_id: conditionName + '_' + this.contexts[conditionName]['id'],
        target: (conditionName == 'concrete' ?
                 tmp_concrete.pop() :
                 tmp_abstract.pop()),
        blockNum : blockNum,
        trialNum : blockNum * 8 + trialInBlock,
        numTrials: this.numTrials,
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
      if(client.game.playerCount == gc.playersThreshold && !gc.paused) {
        _.map(all, p => p.player.instance.emit( 'colorReceived', {
          user: client.userid, id: message_parts[1]
        }));
      }
      break;

    case 'finishedPretest' :
      target.ready = true;
      //console.log(_.map(all, p => p.player));
      console.log('num players', all.length);
      console.log('ready vector', _.map(all, p => p.player.ready))
      if(_.every(all, p => p.player.ready))
        gc.newRound(3000);
      break;
      
    case 'sendResponse' :
      _.map(all, p => p.player.instance.emit('updateScore', {
        outcome: message_parts[1]
      }));
      gc.newRound(3000);
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

module.exports = ServerRefGame;
