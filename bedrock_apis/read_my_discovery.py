import boto3
import json
from typing import Dict, Any
import os


def read_discovery_table(region: str) -> Dict[str, Any]:
    """
    Read all items from the discovery DynamoDB table.
    
    Args:
        region: AWS region
        
    Returns:
        Dict containing all items from the table

    """

    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('discovery')
    
    # Scan the entire table
    response = table.scan()
    items = response.get('Items', [])
    
    # Handle pagination if there are more items
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    return {
        'total_items': len(items),
        'items': items
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event (dict): Lambda event data containing:
            - region: AWS region (optional, defaults to us-east-1)
        context: Lambda context
        
    Returns:
        Dict containing all items from discovery table
    """

    #Setting parameters from Bedrock agent
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Get region from event or use default
    region = event.get('region', 'us-east-1')
    response = read_discovery_table(region)
    try:
        result = {
            'actionGroup': event['actionGroup'],
            'function': event['function'],
            'functionResponse': {
                'responseBody': {
                    "TEXT": {
                        "body": json.dumps(response, indent=2, default=str)
                    }
                }
            }
        } 
        print(result)
        
 

        action_response = {
            'messageVersion': '1.0', 
            'response': result,
        }
        print(action_response)

        return action_response
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }
