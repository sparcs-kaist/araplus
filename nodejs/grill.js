var express = require('express');
var http = require('http');
var app = express();

var server = http.createServer(app);

var io = require('socket.io').listen(server);
server.listen(9779);

// var cookie_reader = require('cookie');
// var querystring = require('querystring');

// var redis = require('socket.io/node_modules/redis');
// var sub = redis.createClient();

var grills = [];

// sub.subscribe('grill');

// accept?


console.log("server open!");
//
io.sockets.on('connection',function(socket){
	var grill;
	// XXX : 여러 그릴에 조인 가능?
	socket.on('adduser', function(grill_id){
		grill = ''+grill_id;
		socket.room = grill;
		socket.join(grill);
		console.log("somebody comes in " + grill);
	})
	
	//Greb message from Redis and send to client
	// sub.on('message',function(channel, message){
	// 	socket.send(message);
	// });

	socket.on('send_message', function(message){
		console.log("message comes in");
		socket.broadcast.to(grill).emit('message', message);
		// values = querystring.stringify({
		// 	comment: message,
		// 	sessionid: socket.handshake.cookie['sessionid'],
		// });

		// var options = {
		// 	host: 'localhost',
		// 	port: 8000, // 서버여는 포트와 같아야한다.
		// 	path: '/node_api',
		// 	method: 'POST',
		// 	headers: {
		// 		'Content-Type': 'application/x-www-form-urlencoded',
		// 		'Content-Length':values.length
		// 	}
		// };

		// // Send message to Django server??
		// var req = http.get(options, function(res){
		// 	res.setEncoding('utf8');

		// 	res.on('data', function(message){
		// 		if(message != 'Everything worked :)'){
		// 			console.log('Message : ' + message);
		// 		}
		// 	});
		// });

		// req.write(values);
		// req.end();
	})
		
})
