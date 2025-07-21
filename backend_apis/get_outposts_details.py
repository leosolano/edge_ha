import json
import boto3
from typing import Dict, List, Any
from decimal import Decimal


def get_outposts_info(region: str) -> Dict[str, Any]:
    """
    Collect information about AWS Outposts in a specific region.
    
    Args:
        region (str): AWS region to query
        
    Returns:
        Dict containing outposts information
    """
    # Initialize clients
    
    outposts_client = boto3.client('outposts', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Get all outposts in the region
    outposts_response = outposts_client.list_outposts(LifeCycleStatusFilter=['ACTIVE'])
    outposts = outposts_response.get('Outposts', [])
    
    result = {}
    
    for outpost in outposts:
        outpost_id = outpost.get('OutpostId')
        outpost_arn = outpost.get('OutpostArn')
        outpost_type = outpost.get('SupportedHardwareType')
        
        # Get outpost instance types
        instance_types_response = outposts_client.get_outpost_instance_types(
            OutpostId=outpost_id
        )
        
        # Get servers for this outpost
        servers_response = outposts_client.list_assets(
            OutpostIdentifier=outpost_id,
            StatusFilter=['ACTIVE']
        )
        
        servers = []
        for asset in servers_response.get('Assets', []):
            asset_info = {
                'AssetId': asset.get('AssetId'),
                'AssetType': asset.get('AssetType'),
                'Status': asset.get('ComputeAttributes',{}).get('State'),
                'Host_Family':asset.get('ComputeAttributes',{}).get('InstanceFamilies'),
                'InstanceType': asset.get('ComputeAttributes',{}).get('InstanceTypeCapacities')
            }
                      
            servers.append(asset_info)

       
        
        result[outpost_id] = {
            'OutpostArn': outpost_arn,
            'Name': outpost.get('Name'),
            'AvailabilityZone': outpost.get('AvailabilityZone'),
            'AvailabilityZoneId': outpost.get('AvailabilityZoneId'),
            'SupportedHardwareType': outpost_type,
            'Servers': servers
        }
    
    return result

def write_to_dynamo(outposts_data: Dict[str, Any], table_name: str, region: str) -> int:
    """
    Write outposts data to DynamoDB table.
    
    Args:
        outposts_data: Data from get_outposts_info
        table_name: DynamoDB table name
        region: AWS region
        
    Returns:
        Number of records written
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    records_written = 0
    
    for outpost_id, outpost_data in outposts_data.items():
                
        # Create DynamoDB item
        item = {
            'edge_id': outpost_id,
            'edge_type': outpost_data.get ('SupportedHardwareType') ,
            'parent_az': outpost_data.get('AvailabilityZoneId'),
            'available_families': outpost_data.get('Servers')
        }
        
        table.put_item(Item=item)
        records_written += 1
    
    return records_written

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event (dict): Lambda event data
        context: Lambda context
        
    Returns:
        Dict containing the results
    """
    # Get region from event or use default
    region = event.get('region', 'us-east-1')
    table_name = 'discovery'
    try:
        outposts_info = get_outposts_info(region)

        # Write to DynamoDB if table_name is provided
        #table_name = event.get('table_name')
        dynamo_result = None
        if table_name:
            records_written = write_to_dynamo(outposts_info, table_name, region)
            dynamo_result = {'records_written': records_written}

        return {
            'statusCode': 200,
            'body': {
                'region': region,
                'outposts': outposts_info,
                'dynamo_result': dynamo_result
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }
