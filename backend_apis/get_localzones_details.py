import boto3
import json
from typing import Dict, List, Any

def get_local_zones_instance_types(region: str) -> Dict[str, Any]:
    """
    Get available Local Zones and their instance type offerings.
    
    Args:
        region (str): AWS region to query
        
    Returns:
        Dict containing Local Zones and their instance types
    """
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Get all availability zones with filter for Local Zones
    az_response = ec2_client.describe_availability_zones(
        Filters=[
            {
                'Name': 'zone-type',
                'Values': ['local-zone']
            }
        ]
    )
    
    result = {}
    
    # Process each Local Zone
    for zone in az_response.get('AvailabilityZones', []):
        zone_name = zone.get('ZoneName')
        zone_id = zone.get('ZoneId')
        parent_az = zone.get('ParentZoneId')
        
        # Get instance types available in this Local Zone
        instance_types_response = ec2_client.describe_instance_type_offerings(
            LocationType='availability-zone',
            Filters=[
                {
                    'Name': 'location',
                    'Values': [zone_name]
                }
            ]
        )
        
        # Extract instance types
        instance_types = [
            offering.get('InstanceType') 
            for offering in instance_types_response.get('InstanceTypeOfferings', [])
        ]
        
        # Add to result dictionary
        result[zone_name] = {
            'ZoneId': zone_id,
            'RegionName': zone.get('RegionName'),
            'ZoneName': zone_name,
            'ParentAZ': parent_az,
            'GroupName': zone.get('GroupName'),
            'NetworkBorderGroup': zone.get('NetworkBorderGroup'),
            'OptInStatus': zone.get('OptInStatus'),
            'InstanceTypes': instance_types
        }
    
    return result

def write_to_dynamo(local_zones_data: Dict[str, Any], table_name: str, region: str) -> int:
    """
    Write local zones data to DynamoDB table.
    
    Args:
        local_zones_data: Data from get_local_zones_instance_types
        table_name: DynamoDB table name
        region: AWS region
        
    Returns:
        Number of records written
    """
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    records_written = 0
    
    for zone_name, zone_data in local_zones_data.items():
        # Parse available families
        available_families = []
        for instance_type in zone_data.get('InstanceTypes', []):
            available_families.append({instance_type: instance_type})
        
        # Create DynamoDB item
        item = {
            'edge_id': zone_data.get('ZoneId'),
            'edge_type': 'Public_LocalZone',
            'parent_az': zone_data.get('ParentAZ'),
            'available_families': available_families
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
    
    try:
        local_zones_info = get_local_zones_instance_types(region)
        # Write to DynamoDB if table_name is provided
        table_name = 'discovery'
        dynamo_result = None
        if table_name:
            records_written = write_to_dynamo(local_zones_info, table_name, region)
            dynamo_result = {'records_written': records_written}

        return {
            'statusCode': 200,
            'body': {
                'region': region,
                'localZones': local_zones_info,
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

