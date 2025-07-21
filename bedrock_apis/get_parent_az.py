import boto3
import json
from typing import Dict, Any
from boto3.dynamodb.conditions import Key

def get_parent_az(edge_id: str, region: str) -> Dict[str, Any]:
    """
    Get parent_az for a given edge_id from DynamoDB.
    
    Args:
        edge_id: Edge infrastructure ID
        table_name: DynamoDB table name
        region: AWS region
        
    Returns:
        Dict containing edge_id and parent_az
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('discovery')
    
    # Query for the specific edge_id
    response = table.query(
        KeyConditionExpression=Key('edge_id').eq(edge_id)
    )
    
    items = response.get('Items', [])
    print(items)
    
    if not items:
        return {
            'edge_id': edge_id,
            'parent_az': None,
            'found': False
        }
        print("no items")
    # Return the first item's parent_az
    item = items[0]
    print(item)
    return {
        'edge_id': edge_id,
        'parent_az': item.get('parent_az'),
        'found': True
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event (dict): Lambda event data containing:
            - edge_id_1: First edge infrastructure ID
            - edge_id_2: Second edge infrastructure ID
            - table_name: DynamoDB table name (optional, defaults to 'discovery')
            - region: AWS region (optional)
        context: Lambda context
        
    Returns:
        Dict containing both edge_ids and their parent_az mappings
    """
    # Get parameters from event
    region = event.get('region', 'us-east-1')

    #Setting parameters from Bedrock agent
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    edge_id_1 = parameters[0].get('value', None)
    edge_id_2 = parameters[1].get('value', None)
    print(edge_id_1)
    print(edge_id_2)
    print(parameters)
    
    # Validate required parameters
    if not all([edge_id_1, edge_id_2]):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Missing required parameters: edge_id_1, edge_id_2'
            })
        }
    
    try:
        # Get parent_az for both edge_ids
        result_1 = get_parent_az(edge_id_1, region)
        result_2 = get_parent_az(edge_id_2, region)
    
        response = {
        'edge_id_1': result_1,
        'edge_id_2': result_2
        } 

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
        print (str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
