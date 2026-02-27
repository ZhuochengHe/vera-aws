**Example 1: To create a VPC**

The following ``create-vpc`` example creates a VPC with the specified IPv4 CIDR block and a Name tag. ::

    aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications ResourceType=vpc,Tags=[{Key=Name,Value=MyVpc}]

Output::

    {
        "Vpc": {
            "CidrBlock": "10.0.0.0/16",
            "DhcpOptionsId": "dopt-5EXAMPLE",
            "State": "pending",
            "VpcId": "vpc-0a60eb65b4EXAMPLE",
            "OwnerId": "123456789012",
            "InstanceTenancy": "default",
            "Ipv6CidrBlockAssociationSet": [],
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-07501b79ecEXAMPLE",
                    "CidrBlock": "10.0.0.0/16",
                    "CidrBlockState": {
                        "State": "associated"
                    }
                }
            ],
            "IsDefault": false,
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "MyVpc"
                }
            ]
        }
    }

**Example 2: To create an internet gateway**

The following ``create-internet-gateway`` example creates an internet gateway with a Name tag. ::

    aws ec2 create-internet-gateway \
        --tag-specifications ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]

Output::

    {
        "InternetGateway": {
            "Attachments": [],
            "InternetGatewayId": "igw-0d0fb496b3994d755",
            "OwnerId": "123456789012",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-igw"
                }
            ]
        }
    }

**Example 3: To attach the internet gateway to the VPC**

The following ``attach-internet-gateway`` example attaches the internet gateway to the specified VPC. ::

    aws ec2 attach-internet-gateway \
        --internet-gateway-id igw-0d0fb496b3994d755 \
        --vpc-id vpc-0a60eb65b4EXAMPLE

**Example 4: To verify the internet gateway is attached to the VPC**

The following ``describe-internet-gateways`` example queries the specified internet gateway's attachment to verify that it is attached to the VPC. ::

    aws ec2 describe-internet-gateways \
        --internet-gateway-ids igw-0d0fb496b3994d755 \
        --query "InternetGateways[0].Attachments"

Output::

    [
        {
            "State": "available",
            "VpcId": "vpc-0a60eb65b4EXAMPLE"
        }
    ]

**Example 5: To create a subnet in the VPC**

The following ``create-subnet`` example creates a subnet in the specified VPC with the specified IPv4 CIDR block. ::

    aws ec2 create-subnet \
        --vpc-id vpc-0a60eb65b4EXAMPLE \
        --cidr-block 10.0.0.0/24 \
        --tag-specifications ResourceType=subnet,Tags=[{Key=Name,Value=my-subnet}]

Output::

    {
        "Subnet": {
            "AvailabilityZone": "us-east-1a",
            "AvailabilityZoneId": "use1-az1",
            "AvailableIpAddressCount": 251,
            "CidrBlock": "10.0.0.0/24",
            "DefaultForAz": false,
            "MapPublicIpOnLaunch": false,
            "State": "available",
            "SubnetId": "subnet-0e99b93155EXAMPLE",
            "VpcId": "vpc-0a60eb65b4EXAMPLE",
            "OwnerId": "123456789012",
            "AssignIpv6AddressOnCreation": false,
            "Ipv6CidrBlockAssociationSet": [],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-subnet"
                }
            ],
            "SubnetArn": "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-0e99b93155EXAMPLE"
        }
    }

