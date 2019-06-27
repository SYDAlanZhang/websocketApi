# Tripsense API
This api project is used for tripsense chat system

## Technology Set
AWS API Gateway
AWS Lambda
AWS Cloudwatch
AWS WebSocket API
AWS dynamoDB
Python 3.7
YAML config file
Serverless Framework
wscat

## Features
Connected through WebSocket API when a user CONNECT or DISCONNECT
The user can send messages to a chatroom and the messages would be sent to all the online uses in that chatroom

# Database Tables
1: Table name: connections
   Primary key: connectionID (String)
   coloums: userId

2: Table name: messages
   Primary key: room (String)
   sort key: index (Number)
   coloums: chatMessage
            createTime
            messageType
            userId

3: Table name: userRoom
   Primary key: userId (String)
   sort key: index (Number)
   coloums: room

# Build up local environment
Download serverless framework and use the framework to deploy it to AWS S3
```
$ npm install serverless -g
$ serverless deploy
```

Install wscat to test websocket api
```
$ npm install -g wscat
```

# Call the API
My api is still online, feel free to call
```
wscat -c wss://40zdzfnfyf.execute-api.ap-southeast-2.amazonaws.com/dev\?userId\={{USERID}}
```
I only add 2 userId: 'uuid1' and 'uuid2' in my dynamoDB, so try to use these two uuid when connecting
('uuid1' is in chatroom: 'uuidroom1' and 'uuidroom2', while 'uuid2' is in chatroom 'uuidroom2' and 'uuidroom3')

So if both 'uuid1' and 'uuid2' are online. If you send messages to 'uuidroom1' and 'uuidroom3', 'uuid1' and 'uuid2' can receive them respectively. if you send messages to 'uuidroom2', both 'uuid' and 'uuid2' can receive them.

Json Format:
```
{
    "action": "sendMessage", 
    "userId": "uuid2", 
    "chatroomId": "uuidroom1", 
    "chatMessage": "See if uuid2 receives", 
    "messageType": "text message"
}
```
# Things I can implement in the future
1. When users try to connect through websocket, check if they are already online. If so, refuse their connect request

2. When a user sending message to a chatroom. Check if this users is in the chatroom. If not, message should not go through

3. Additional questions: (when user is offline)
I seperate the index id in the message table, so each chatroom has its own message index.
eg: chatroom1 could have message indexes 1,2,3,4,5. While chatroom2 could have indexes 1,2,3,4

When a user DISCONNECT, just record the largest message indexes of each chatroom for this user in a table.
eg: uuid1: {chatroom1: 5, chatroom2: 4}

When this user CONNECT again. Compare the index we record in the database and the current index. The largest index for each chatroom could become: {chatroom1: 10, chatroom2: 9}
So just write a function to return the message between these indexes: {chatroom1: 6-10, chatroom2: 5-9}

4. Add AWS SQS to handle the task queue
I didn't involve this in this project, but it could be a good practise to do it in the future.

# Things I have learnt from this project
I haven't used websocket api and nosql database before. After this exercise, I realize the advantages of websocket api compare to RESTful api. And Also the advantages of nosql database compare to a traditional SQL based database.
This project also increased my knowledge of AWS formation system and python development.

Thank you!