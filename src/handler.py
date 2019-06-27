import boto3
import time
import json
import logging

import helper

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource("dynamodb")

def connection_handler(event, context):
    """
    This function is used for handling connection related requests:
    EVENTTYPE could be 'CONNECT', 'DISCONNECT' OR 'UNKNOW'
    """
    connectionId = event["requestContext"]["connectionId"]
    connectionTable = dynamodb.Table("connections")
 
    userId = event["queryStringParameters"]["userId"] if ("queryStringParameters" in event) else "UNKNOWN USER"
    
    if event["requestContext"]["eventType"] == "CONNECT":
        logger.info("*** A client is requesting for CONNECT ***")
        logger.debug(event)
        connectionTable.put_item(Item={"connectionID": connectionId,
                                       "userId": userId})
        return helper.json_response(200, "Successfully connected.")
    elif event["requestContext"]["eventType"] == "DISCONNECT":
        logger.info("*** A client is requesting for DIDCONNECT ***")
        logger.debug(event)
        connectionTable.delete_item(Key={"connectionID": connectionId})
        return helper.json_response(200, "Successfully disconnected.")     
    else:
        logger.error("Unknown EventType.")
        return helper.json_response(500, "Internal server error.")

def default_message(event, context):
    """
    When Websocket connection Eventtype is not known (not CONNECT or DISCONNECT)
    """
    logger.error("Unknown Websocket Connection Type")
    return helper.json_response(400, "Unknown Websocket Connection Type")

def send_message(event, context):
    """
    This function get the users in the chatroom and also the users who are online
    Make an AND operation and get all the connections we should send a message to
    """
    logger.info("Start sending a message.")
    requestKey = ["userId", "chatroomId", "chatMessage", "messageType"]
    body = json.loads(event.get("body", ""))
    messageTable = dynamodb.Table("messages")
    connectionTable = dynamodb.Table("connections")
    userRoomTable = dynamodb.Table("userRoom")

    if not helper.check_json_key(body, requestKey):
        return helper.json_response(400, "Missing request json key")
    
    userId, chatMessage, messageType, chatroomId = body["userId"], body["chatMessage"], body["messageType"], str(body["chatroomId"])
    currentTimestamp = int(time.time())
    logger.info(chatroomId)

    indexResponse = messageTable.query(KeyConditionExpression="room = :room",
                                  ExpressionAttributeValues={":room": chatroomId},
                                  Limit=1, 
                                  ScanIndexForward=False)

    items = indexResponse["Items"]
    index = 1
    if len(items) > 0:
        index = items[0]["index"] + 1

    messageTable.put_item(Item={"room": chatroomId, 
                                "index": index,
                                "createdTime": currentTimestamp, 
                                "userId": userId,
                                "chatMessage": chatMessage,
                                "messageType": messageType})

    connectionAndUserId = connectionTable.scan().get("Items", [])
    userIdAndRoom = userRoomTable.scan().get("Items", [])
    roomUser = []
    connections = []

    for i in userIdAndRoom:
        if i["room"] == chatroomId:
            roomUser.append(i["userId"])
    for k in connectionAndUserId:
        if k["userId"] in roomUser:
            connections.append(k["connectionID"])

    logger.info(connectionAndUserId)
    logger.info(userIdAndRoom)
    logger.info(roomUser)
    logger.info(connections)

    responseMessage = {"userId": userId, 
                       "chatroomId": chatroomId, 
                       "chatMessage": chatMessage,
                       "messageType": messageType}
    for connectionID in connections:
        helper.send_to_connections(connectionID, {"messages": [responseMessage]}, event)

    logger.info("Finish sending a message")
    return helper.json_response(200, "Message sent to all users in room: {}".format(chatroomId))
