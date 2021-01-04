var _ = require('lodash');
var fs    = require('fs');
var assert = require('assert');
var utils  = require(__base + 'src/sharedUtils.js');
var ServerGame = require(__base + 'src/game.js')['ServerGame'];
const contextPath = '../../data/contexts/radius-sampling/';

class ServerRefGame extends ServerGame {
  constructor(config) {
    super(config);
    const concretes = _.clone(_.sampleSize(require(`${contextPath}/concrete-contexts.json`), 2));
    const abstracts = _.clone(_.sampleSize(require(`${contextPath}/abstract-contexts.json`), 2));
    this.contexts = {'concrete' : concretes[0], 'abstract' : abstracts[0]};
    this.controls = {'concrete' : concretes[1], 'abstract' : abstracts[1]};
    this.numBlocks = 6;
    this.numTrialsInBlock = 8;
    this.ready = false;
    this.numTrials = this.numBlocks * this.numTrialsInBlock + 2;
    this.numRounds = this.numBlocks * this.numTrialsInBlock + 2;    
    this.firstRole = _.sample(['speaker', 'listener']);
    this.trialList = this.makeTrialList();
  }

  customEvents (socket) {  }

  // *
  // * TrialList creation
  // *

  getRandomizedConditions() {
    const numEach = this.numTrialsInBlock / 2;
    const conditions = [].concat(
      utils.fillArray("concrete", numEach),
      utils.fillArray("abstract", numEach)
    );
    return _.shuffle(conditions);
  };

  makeTrialList () {
    let trialList = [];
    trialList.push(this.makeTestSequence('pre'));
    _.forEach(_.range(this.numBlocks), blockNum => {
      trialList.push(...this.sampleBlock(blockNum));
    });
    trialList.push(this.makeTestSequence('post'));
    return(trialList);
  };
  
  makeTestSequence (phase){
    let wordSeq = [];
    _.forEach(['concrete', 'abstract'], condition => {
      _.forEach(['test', 'control'], set => {
        const words = (set == 'test' ? this.contexts[condition]['words'] :
                       this.controls[condition]['words']);
        _.forEach(words, word => {
          wordSeq.push({phase: phase, target: word, condition: condition, set: set});
        });
      });
    });
    wordSeq.push({target: phase == 'pre' ? 'blue' : 'red',
                  phase: phase, condition: 'catch', set: 'catch'});
    return {
      phase: phase,
      numTrials: wordSeq.length,
      roles: _.zipObject(_.map(this.players, p => p.id), ['picker', 'picker']),
      trialSeq : wordSeq
    };
  }
  
  sampleBlock (blockNum) {
    var conditionList = this.getRandomizedConditions();
    var tmp_concrete = _.shuffle(_.clone(this.contexts['concrete']['words']));
    var tmp_abstract = _.shuffle(_.clone(this.contexts['abstract']['words']));
    return _.map(conditionList, (conditionName, trialInBlock) => {
      var roleNames = _.values(this.playerRoleNames);
      var blockAssignment = blockNum % 2 == 0 ? roleNames : _.reverse(roleNames);
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
        roles: _.zipObject(_.map(this.players, p => p.id), blockAssignment)
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
  dataOutput () {}
}
  //   function commonOutput (client, message_data) {
  //     //var target = client.game.currStim.target;
  //     //var distractor = target == 'g1' ? 'g0' : 'g1';
  //     return {
  //    // targetGoalSet: client.game.currStim.goalSets[target],
  //    // distractorGoalSet: client.game.currStim.goalSets[distractor],
  //    firstRole: client.game.firstRole
  //     };
  //   };



  //   var exitSurveyOutput = function(client, message_data) {
  //     var subjInfo = JSON.parse(message_data.slice(1));
  //     return _.extend(
  //    _.omit(commonOutput(client, message_data),
  //           ['targetGoalSet', 'distractorGoalSet', 'trialType', 'trialNum']),
  //    subjInfo);
  //   };

  //   var responseOutput = function(client, message_data) {
  //     var selections = message_data.slice(3);
  //     var allObjs = client.game.currStim.hiddenCards;
  //     return _.extend(
  //    commonOutput(client, message_data), {
  //      sender: message_data[1],
  //      timeFromMessage: message_data[2],
  //      revealedObjs : selections,
  //      numRevealed : selections.length,
  //      fullContext: 
  //    });
  //   };

  //   return {
  //     'sendResponse' : responseOutput,
  //     'exitSurvey' : exitSurveyOutput
  //   };
  // }}

module.exports = ServerRefGame;
