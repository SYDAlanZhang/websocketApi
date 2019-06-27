import boto3
import json
import logging

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

def json_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}

def check_json_key(body, requestKey):
    for ele in requestKey:
        if ele not in body:
            logger.info("Missing request json key: {}".format(ele))
            return False
    return True

def send_to_connections(connectionId, data, event):
    """
    Send messages based on connectionIDs
    """
    apiGateway = boto3.client("apigatewaymanagementapi",
                              endpoint_url = "https://{}/{}".format(event["requestContext"]["domainName"], 
                                                                    event["requestContext"]["stage"]))
    return apiGateway.post_to_connection(ConnectionId=connectionId, Data=json.dumps(data).encode('utf-8'))