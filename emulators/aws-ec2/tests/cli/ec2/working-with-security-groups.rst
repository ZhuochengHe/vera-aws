**Example 1: To create a security group for a VPC**

The following ``create-security-group`` example creates a security group for the specified VPC. ::

    aws ec2 create-security-group \
        --group-name my-sg \
        --description "My security group" \
        --vpc-id vpc-1a2b3c4d

Output::

    {
        "GroupId": "sg-903004f8"
    }

**Example 2: To describe a security group**

The following ``describe-security-groups`` example describes the specified security group. ::

    aws ec2 describe-security-groups \
        --group-ids sg-903004f8

Output::

    {
        "SecurityGroups": [
            {
                "IpPermissionsEgress": [
                    {
                        "IpProtocol": "-1",
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "UserIdGroupPairs": []
                    }
                ],
                "Description": "My security group",
                "IpPermissions": [],
                "GroupName": "my-sg",
                "VpcId": "vpc-1a2b3c4d",
                "OwnerId": "123456789012",
                "GroupId": "sg-903004f8"
            }
        ]
    }

**Example 3: To add a rule that allows inbound RDP traffic**

The following ``authorize-security-group-ingress`` example adds a rule that allows inbound traffic on TCP port 3389 (RDP) from the specified IP address. ::

    aws ec2 authorize-security-group-ingress \
        --group-id sg-903004f8 \
        --protocol tcp \
        --port 3389 \
        --cidr x.x.x.x/x

**Example 4: To add a rule that allows inbound SSH traffic**

The following ``authorize-security-group-ingress`` example adds a rule that allows inbound traffic on TCP port 22 (SSH) from the specified IP address. ::

    aws ec2 authorize-security-group-ingress \
        --group-id sg-903004f8 \
        --protocol tcp \
        --port 22 \
        --cidr x.x.x.x/x

**Example 5: To describe a security group after adding inbound rules**

The following ``describe-security-groups`` example describes the specified security group after adding inbound rules. ::

    aws ec2 describe-security-groups \
        --group-ids sg-903004f8

Output::

    {
        "SecurityGroups": [
            {
                "IpPermissionsEgress": [
                    {
                        "IpProtocol": "-1",
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "UserIdGroupPairs": []
                    }
                ],
                "Description": "My security group",
                "IpPermissions": [
                    {
                        "ToPort": 22,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {
                                "CidrIp": "x.x.x.x/x"
                            }
                        ],
                        "UserIdGroupPairs": [],
                        "FromPort": 22
                    }
                ],
                "GroupName": "my-sg",
                "OwnerId": "123456789012",
                "GroupId": "sg-903004f8"
            }
        ]
    }

For more information, see `Creating, configuring, and deleting Amazon EC2 security groups in the AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-services-ec2-sg.html>`
