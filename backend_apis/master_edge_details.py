import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Master lambda function that synchronously calls two other lambdas:
    - get_outposts_details
    - get_localzones_details
    """
    
    lambda_client = boto3.client('lambda')
    
    results = {
        'outposts': None,
        'localzones': None,
        'errors': []
    }
    
    try:
        # Call get_outposts_details lambda synchronously
        outposts_response = lambda_client.invoke(
            FunctionName='get_outposts_details',
            InvocationType='RequestResponse',  # Synchronous invocation
            Payload=json.dumps(event)
        )
        
        # Parse the response
        outposts_payload = json.loads(outposts_response['Payload'].read())
        
        if outposts_response['StatusCode'] == 200:
            results['outposts'] = outposts_payload
        else:
            results['errors'].append(f"Outposts lambda failed with status: {outposts_response['StatusCode']}")
            
    except ClientError as e:
        results['errors'].append(f"Error calling get_outposts_details: {str(e)}")
    except Exception as e:
        results['errors'].append(f"Unexpected error calling get_outposts_details: {str(e)}")
    
    try:
        # Call get_localzones_details lambda synchronously
        localzones_response = lambda_client.invoke(
            FunctionName='get_localzones_details',
            InvocationType='RequestResponse',  # Synchronous invocation
            Payload=json.dumps(event)
        )
        
        # Parse the response
        localzones_payload = json.loads(localzones_response['Payload'].read())
        
        if localzones_response['StatusCode'] == 200:
            results['localzones'] = localzones_payload
        else:
            results['errors'].append(f"Local zones lambda failed with status: {localzones_response['StatusCode']}")
            
    except ClientError as e:
        results['errors'].append(f"Error calling get_localzones_details: {str(e)}")
    except Exception as e:
        results['errors'].append(f"Unexpected error calling get_localzones_details: {str(e)}")
    
    # Determine overall success
    success = len(results['errors']) == 0
    
    if success:
        # Parse and format the response data
        formatted_response = parse_edge_discovery_data(results)
        return {
            'statusCode': 200,
            'body': json.dumps(formatted_response)
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'errors': results['errors'],
                'message': 'Edge discovery completed with errors'
            })
        }


def parse_edge_discovery_data(results):
    """
    Parse the raw lambda responses and format them according to the required structure
    """
    answer = {
        "public_local_zones": [],
        "outposts": {}
    }
    
    # Parse Local Zones data
    if results['localzones'] and 'body' in results['localzones']:
        lz_data = results['localzones']['body']
        if 'localZones' in lz_data:
            for zone_name, zone_info in lz_data['localZones'].items():
                # Extract instance type families
                c_family, m_family, r_family = extract_instance_families(zone_info.get('InstanceTypes', []))
                
                local_zone = {
                    "edge_id": zone_name,
                    "parent_region": zone_info.get('RegionName', ''),
                    "parent_az": zone_info.get('ParentAZ', ''),
                    "c_family": c_family,
                    "m_family": m_family,
                    "r_family": r_family
                }
                answer["public_local_zones"].append(local_zone)
    
    # Parse Outposts data
    if results['outposts'] and 'body' in results['outposts']:
        op_data = results['outposts']['body']
        if 'outposts' in op_data:
            # Get the first outpost (assuming single outpost for now)
            for outpost_id, outpost_info in op_data['outposts'].items():
                # Extract instance types from servers
                all_instance_types = []
                for server in outpost_info.get('Servers', []):
                    for instance_type_info in server.get('InstanceType', []):
                        all_instance_types.append(instance_type_info['InstanceType'])
                
                # Extract instance type families
                c_family, m_family, r_family = extract_instance_families(all_instance_types)
                
                answer["outposts"] = {
                    "edge_id": outpost_id,
                    "parent_region": op_data.get('region', ''),
                    "parent_az": outpost_info.get('AvailabilityZone', ''),
                    "c_family": c_family,
                    "m_family": m_family,
                    "r_family": r_family
                }
                break  # Take first outpost
    
    return {"answer": answer}


def extract_instance_families(instance_types):
    """
    Extract and categorize instance types by family (c, m, r) and size
    """
    c_family = set()
    m_family = set()
    r_family = set()
    
    for instance_type in instance_types:
        if not instance_type:
            continue
            
        # Parse instance type (e.g., "c6i.4xlarge" -> family="c", size="4xlarge")
        parts = instance_type.split('.')
        if len(parts) >= 2:
            family_part = parts[0]  # e.g., "c6i"
            size = parts[1]         # e.g., "4xlarge"
            
            # Determine family based on first character
            if family_part.startswith('c'):
                c_family.add(size)
            elif family_part.startswith('m'):
                m_family.add(size)
            elif family_part.startswith('r'):
                r_family.add(size)
    
    # Convert sets to sorted lists
    return sorted(list(c_family)), sorted(list(m_family)), sorted(list(r_family))
