**Example 1: To create a key pair**

The following ``create-key-pair`` example creates a key pair named ``MyKeyPair`` and saves the private key to a local PEM file. ::

    aws ec2 create-key-pair \
        --key-name MyKeyPair \
        --query "KeyMaterial" \
        --output text > MyKeyPair.pem

**Example 2: To verify the key pair was created**

The following ``describe-key-pairs`` example describes the newly created key pair to verify it exists. ::

    aws ec2 describe-key-pairs \
        --key-names MyKeyPair

Output::

    {
        "KeyPairs": [
            {
                "KeyPairId": "key-0b94643da6EXAMPLE",
                "KeyFingerprint": "1f:51:ae:28:bf:89:e9:d8:1f:25:5d:37:2d:7d:b8:ca:9f:f5:f1:6f",
                "KeyName": "MyKeyPair",
                "KeyType": "rsa",
                "Tags": [],
                "CreateTime": "YYYY-MM-DDTHH:MM:SS.000Z"
            }
        ]
    }

**Example 3: To launch an instance with the key pair**

The following ``run-instances`` example launches a ``t2.micro`` instance using the newly created key pair. ::

    aws ec2 run-instances \
        --image-id ami-xxxxxxxx \
        --count 1 \
        --instance-type t2.micro \
        --key-name MyKeyPair \
        --security-group-ids sg-903004f8 \
        --subnet-id subnet-6e7f829e

Output::

    {
        "Instances": [
            {
                "AmiLaunchIndex": 0,
                "ImageId": "ami-xxxxxxxx",
                "InstanceId": "i-5203422c",
                "InstanceType": "t2.micro",
                "KeyName": "MyKeyPair",
                "LaunchTime": "YYYY-MM-DDTHH:MM:SS.000Z",
                "Monitoring": {
                    "State": "disabled"
                },
                "Placement": {
                    "AvailabilityZone": "us-east-1a",
                    "GroupName": "",
                    "Tenancy": "default"
                },
                "PrivateDnsName": "ip-10-0-0-157.us-east-1.compute.internal",
                "PrivateIpAddress": "10.0.0.157",
                "ProductCodes": [],
                "PublicDnsName": "",
                "State": {
                    "Code": 0,
                    "Name": "pending"
                },
                "StateTransitionReason": "",
                "SubnetId": "subnet-6e7f829e",
                "VpcId": "vpc-1a2b3c4d",
                "Architecture": "x86_64",
                "BlockDeviceMappings": [],
                "ClientToken": "",
                "EbsOptimized": false,
                "Hypervisor": "xen",
                "NetworkInterfaces": [
                    {
                        "Attachment": {
                            "AttachTime": "YYYY-MM-DDTHH:MM:SS.000Z",
                            "AttachmentId": "eni-attach-0e325c07e928a0405",
                            "DeleteOnTermination": true,
                            "DeviceIndex": 0,
                            "Status": "attaching"
                        },
                        "Description": "",
                        "Groups": [
                            {
                                "GroupName": "MySecurityGroup",
                                "GroupId": "sg-903004f8"
                            }
                        ],
                        "Ipv6Addresses": [],
                        "MacAddress": "0a:ab:58:e0:67:e2",
                        "NetworkInterfaceId": "eni-0c0a29997760baee7",
                        "OwnerId": "123456789012",
                        "PrivateDnsName": "ip-10-0-0-157.us-east-1.compute.internal",
                        "PrivateIpAddress": "10.0.0.157",
                        "PrivateIpAddresses": [
                            {
                                "Primary": true,
                                "PrivateDnsName": "ip-10-0-0-157.us-east-1.compute.internal",
                                "PrivateIpAddress": "10.0.0.157"
                            }
                        ],
                        "SourceDestCheck": true,
                        "Status": "in-use",
                        "SubnetId": "subnet-6e7f829e",
                        "VpcId": "vpc-1a2b3c4d",
                        "InterfaceType": "interface"
                    }
                ],
                "RootDeviceName": "/dev/xvda",
                "RootDeviceType": "ebs",
                "SecurityGroups": [
                    {
                        "GroupName": "MySecurityGroup",
                        "GroupId": "sg-903004f8"
                    }
                ],
                "SourceDestCheck": true,
                "StateReason": {
                    "Code": "pending",
                    "Message": "pending"
                },
                "Tags": [],
                "VirtualizationType": "hvm",
                "CpuOptions": {
                    "CoreCount": 1,
                    "ThreadsPerCore": 1
                },
                "CapacityReservationSpecification": {
                    "CapacityReservationPreference": "open"
                },
                "MetadataOptions": {
                    "State": "pending",
                    "HttpTokens": "optional",
                    "HttpPutResponseHopLimit": 1,
                    "HttpEndpoint": "enabled"
                }
            }
        ],
        "OwnerId": "123456789012",
        "ReservationId": "r-5875ca20"
    }

**Example 4: To wait until the instance is running**

The following ``wait instance-running`` example pauses until the instance is running. It produces no output. ::

    aws ec2 wait instance-running \
        --instance-ids i-5203422c

**Example 5: To verify the instance is using the key pair**

The following ``describe-instances`` example queries the instance to confirm the key pair name and running state. ::

    aws ec2 describe-instances \
        --instance-ids i-5203422c \
        --query "Reservations[0].Instances[0].{InstanceId:InstanceId,KeyName:KeyName,State:State.Name}"

Output::

    {
        "InstanceId": "i-5203422c",
        "KeyName": "MyKeyPair",
        "State": "running"
    }

**Example 6: To stop the instance**

The following ``stop-instances`` example stops the running instance before cleanup. ::

    aws ec2 stop-instances \
        --instance-ids i-5203422c

Output::

    {
        "StoppingInstances": [
            {
                "InstanceId": "i-5203422c",
                "CurrentState": {
                    "Code": 64,
                    "Name": "stopping"
                },
                "PreviousState": {
                    "Code": 16,
                    "Name": "running"
                }
            }
        ]
    }

**Example 7: To wait until the instance is stopped**

The following ``wait instance-stopped`` example pauses until the instance is fully stopped. It produces no output. ::

    aws ec2 wait instance-stopped \
        --instance-ids i-5203422c

**Example 8: To terminate the instance**

The following ``terminate-instances`` example terminates the stopped instance. ::

    aws ec2 terminate-instances \
        --instance-ids i-5203422c

Output::

    {
        "TerminatingInstances": [
            {
                "InstanceId": "i-5203422c",
                "CurrentState": {
                    "Code": 32,
                    "Name": "shutting-down"
                },
                "PreviousState": {
                    "Code": 80,
                    "Name": "stopped"
                }
            }
        ]
    }

**Example 9: To delete the key pair**

The following ``delete-key-pair`` example deletes the key pair after the instance is terminated. ::

    aws ec2 delete-key-pair \
        --key-name MyKeyPair

Output::

    {
        "Return": true,
        "KeyPairId": "key-0b94643da6EXAMPLE"
    }
