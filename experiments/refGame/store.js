'use strict';

const _ = require('lodash');
const bodyParser = require('body-parser');
const express = require('express');
const fs = require('fs');
const mongodb = require('mongodb');
const path = require('path');
const sendPostRequest = require('request').post;
const colors = require('colors/safe');

const app = express();
const MongoClient = mongodb.MongoClient;
const port = 6004;
const mongoCreds = require('./auth.json');
const mongoURL = `mongodb://${mongoCreds.user}:${mongoCreds.password}@localhost:27017/`;
const handlers = {};


function makeMessage(text) {
  return `${colors.blue('[store]')} ${text}`;
}

function log(text) {
  console.log(makeMessage(text));
}

function error(text) {
  console.error(makeMessage(text));
}

function failure(response, text) {
  const message = makeMessage(text);
  console.error(message);
  return response.status(500).send(message);
}

function success(response, text) {
  const message = makeMessage(text);
  console.log(message);
  return response.send(message);
}

function mongoConnectWithRetry(delayInMilliseconds, callback) {
  MongoClient.connect(mongoURL, (err, connection) => {
    if (err) {
      console.error(`Error connecting to MongoDB: ${err}`);
      setTimeout(() => mongoConnectWithRetry(delayInMilliseconds, callback), delayInMilliseconds);
    } else {
      log('connected succesfully to mongodb');
      callback(connection);
    }
  });
}

async function retrieveCondition(coll, condition, gameid, callback) {
  // Find entry with min number of games
  const minGame = await coll.findOne({}, {sort: {numGames: 1, limit: 1}});

  // Get the total number of entries with that min number
  const size = await coll.count({
    condition: condition,
    numGames: minGame['numGames']
  });

  // Generate an integer n between 0 and that number
  const random = Math.floor(Math.random() * size);

  // Use skip to pick the nth entry (i.e. random context)
  const context = await coll.findOne(
    {condition: condition, numGames: minGame['numGames']},
    {sort: { numGames : 1 }, limit : 1, skip: random}
  );

  // Increment number of games for the chosen context and return
  coll.updateOne(
    {id: context['id']},
    {$push : {games : gameid}, $inc  : {numGames : 1}},
    (err, result) => {callback(context);}
  );
}

function serve() {

  mongoConnectWithRetry(2000, (connection) => {

    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true }));

    app.post('/db/exists', (request, response) => {            

      if (!request.body) {
        return failure(response, '/db/exists needs post request body');
      }
      const databaseName = request.body.dbname;
      const database = connection.db(databaseName);
      const query = request.body.query;
      const projection = request.body.projection;

      // hardcoded for now (TODO: get list of collections in db)
      var collectionList = ['word-color-priors', 'ref-game']; 

      function checkCollectionForHits(collectionName, query, projection, callback) {
        const collection = database.collection(collectionName);        
        collection.find(query, projection).limit(1).toArray((err, items) => {          
          callback(!_.isEmpty(items));
        });
      }

      function checkEach(collectionList, checkCollectionForHits, query,
			 projection, evaluateTally) {
        var doneCounter = 0;
        var results = 0;          
        collectionList.forEach(function (collectionName) {
          checkCollectionForHits(collectionName, query, projection, function (res) {
            log(`got request to find_one in ${collectionName} with` +
                ` query ${JSON.stringify(query)} and projection ${JSON.stringify(projection)}`);          
            doneCounter += 1;
            results+=res;
            if (doneCounter === collectionList.length) {
              evaluateTally(results);
            }
          });
        });
      }
      function evaluateTally(hits) {
        console.log("hits: ", hits);
        response.json(hits>0);
      }
      checkEach(collectionList, checkCollectionForHits, query, projection, evaluateTally);

      // // Always let the requester test ;) // this is handled by blockResearchers flag in app.js
      // if(_.includes(['A1BOIDKD33QSDK', 'A4SSYO0HDVD4E', 'A1MMCS8S8CTWKU'],
		    // query.workerId)) {
	     //   response.json(false);
      // } else {
	     //   checkEach(collectionList, checkCollectionForHits, query, projection, evaluateTally);
      // }
    });

    app.post('/db/insert', (request, response) => {
      if (!request.body) {
        return failure(response, '/db/insert needs post request body');
      }
      log(`got request to insert into ${request.body.colname}`);
      
      const databaseName = request.body.dbname;
      const collectionName = request.body.colname;
      if (!collectionName) {
        return failure(response, '/db/insert needs collection');
      }
      if (!databaseName) {
        return failure(response, '/db/insert needs database');
      }

      const database = connection.db(databaseName);
      
      // Add collection if it doesn't already exist
      if (!database.collection(collectionName)) {
        console.log('creating collection ' + collectionName);
        database.createCollection(collectionName);
      }

      const collection = database.collection(collectionName);

      const data = _.omit(request.body, ['colname', 'dbname']);
      // log(`inserting data: ${JSON.stringify(data)}`);
      collection.insert(data, (err, result) => {
        if (err) {
          return failure(response, `error inserting data: ${err}`);
        } else {
          return success(response, `successfully inserted data. result: ${JSON.stringify(result)}`);
        }
      });
    });

    app.post('/db/getstims', (request, response) => {
      if (!request.body) {
	return failure(response, '/db/getstims needs post request body');
      }
      console.log(`got request to get stims from ${request.body.dbname}/${request.body.colname}`);

      const databaseName = request.body.dbname;
      const collectionName = request.body.colname;
      if (!collectionName) {
	return failure(response, '/db/getstims needs collection');
      }
      if (!databaseName) {
	return failure(response, '/db/getstims needs database');
      }

      const database = connection.db(databaseName);
      const collection = database.collection(collectionName);

      // sort by number of times previously served up and take the first
      retrieveCondition(collection, 'concrete', request.body.gameid, (concreteResults) => {
	retrieveCondition(collection, 'abstract', request.body.gameid, (abstractResults) => {
	  response.send({
	    'concrete': concreteResults,
	    'abstract' : abstractResults
	  });
	});
      });
    });
    
    
    app.listen(port, () => {
      log(`running at http://localhost:${port}`);
    });
    
  });
  
}

serve();
