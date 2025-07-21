# Hybrid and Edge Resiliency Tool

## Introduction

The Hybrid and Edge Resiliency Tool is a powerful application built on the Cloudscape design platform that helps you discover, analyze, and optimize your Hybrid and Edge infrastructure on AWS. This tool enables you to:

- Discover your existing Edge infrastructure components
- Create High Availability Groups (HA_Groups) at the Edge
- Ensure anti-affinity configurations with respect to Parent Availability Zones
- Validate compute capacity requirements for maintaining application quorum
- Receive natural language explanations powered by Amazon Bedrock
- Generate ready-to-deploy CloudFormation templates

## Workflow

### Step 1: Infrastructure Discovery

The application begins by discovering your existing Hybrid and Edge infrastructure components through an API call.

**Technical Details:**
- API Gateway: `Discovery` stage
- Resource: `/edge`
- Method: `GET`
- Backend: `master_edge_details` Lambda function

This process scans your AWS account to identify all Edge infrastructure components including AWS Outposts, Local Zones, and their respective configurations.

### Step 2: Dashboard Population

After discovery completes, the application populates a comprehensive dashboard displaying your Edge infrastructure details.

**Technical Details:**
- API Gateway: `Discovery` stage
- Resource: `/dashboard`
- Method: `GET`

The dashboard provides a visual representation of your:
- Edge infrastructure components
- Parent Availability Zone relationships
- Current capacity utilization
- Existing configurations

### Step 3: Intent-Based Architecture

This step enables you to create and validate High Availability Groups for your Edge infrastructure.

**Key Features:**
- Select and pair Edge infrastructure components (Outposts, Local Zones)
- Validate instance type and size availability across selected components
- For Outposts: Verify available slotting capacity
- Ensure Parent AZ anti-affinity for true high availability
- Receive intelligent recommendations powered by Amazon Bedrock agent

The Intent-Based Architecture tab helps you design resilient Edge deployments that maintain application quorum even during infrastructure failures.

### Step 4: CloudFormation Template Generation

Once you've designed your HA architecture, you can generate a CloudFormation template for immediate deployment.

**Requirements:**
- Provide VPC CIDR(s) for the deployment
- Click the "Download CloudFormation Template" button

The generated template includes:
- Properly configured VPC resources
- Subnet allocations optimized for HA
- Security group configurations
- Edge infrastructure resource allocations
- Routing configurations for optimal connectivity

## Getting Started

1. Ensure you have appropriate permissions to discover Edge infrastructure in your AWS account
2. Access the Hybrid and Edge Resiliency Tool through the provided URL
3. Follow the step-by-step workflow outlined above
4. Review recommendations and download the CloudFormation template
5. Deploy the template in your AWS account

## Architecture Diagram



## Benefits

- **Simplified Discovery**: Automatically identify all Edge infrastructure components
- **Intelligent Pairing**: Create optimal HA Groups with Parent AZ anti-affinity
- **Capacity Validation**: Ensure sufficient compute resources for application quorum
- **Natural Language Explanations**: Understand recommendations through AI-powered descriptions
- **Accelerated Deployment**: Generate ready-to-use CloudFormation templates

## Technical Requirements

- AWS Account with Edge infrastructure components (Outposts, Local Zones)
- Appropriate IAM permissions for discovery and template generation
- Modern web browser supporting Cloudscape Design System

## Support

For questions or assistance, please contact the Hybrid and Edge Resiliency Tool team.


