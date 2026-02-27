**Example 1: To launch an instance**

The following ``run-instances`` example launches a ``t2.micro`` instance that will be used to attach an EBS volume. ::

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

**Example 2: To wait until the instance is running**

The following ``wait instance-running`` example pauses until the instance is running. It produces no output. ::

    aws ec2 wait instance-running \
        --instance-ids i-5203422c

**Example 3: To create an EBS volume**

The following ``create-volume`` example creates a 20 GiB General Purpose SSD (gp2) volume in the specified Availability Zone. ::

    aws ec2 create-volume \
        --volume-type gp2 \
        --size 20 \
        --availability-zone us-east-1a \
        --tag-specifications ResourceType=volume,Tags=[{Key=Name,Value=MyDataVolume}]

Output::

    {
        "AvailabilityZone": "us-east-1a",
        "Tags": [
            {
                "Key": "Name",
                "Value": "MyDataVolume"
            }
        ],
        "Encrypted": false,
        "VolumeType": "gp2",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "creating",
        "Iops": 100,
        "SnapshotId": "",
        "CreateTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "Size": 20
    }

**Example 4: To wait until the volume is available**

The following ``wait volume-available`` example pauses until the volume is available for attachment. It produces no output. ::

    aws ec2 wait volume-available \
        --volume-ids vol-1234567890abcdef0

**Example 5: To attach the volume to the instance**

The following ``attach-volume`` example attaches the volume to the instance as ``/dev/sdf``. ::

    aws ec2 attach-volume \
        --volume-id vol-1234567890abcdef0 \
        --instance-id i-5203422c \
        --device /dev/sdf

Output::

    {
        "AttachTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "InstanceId": "i-5203422c",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "attaching",
        "Device": "/dev/sdf"
    }

**Example 6: To verify the volume is attached**

The following ``describe-volumes`` example queries the volume to verify it is in the ``in-use`` state and attached to the instance. ::

    aws ec2 describe-volumes \
        --volume-ids vol-1234567890abcdef0 \
        --query "Volumes[0].{State:State,InstanceId:Attachments[0].InstanceId,Device:Attachments[0].Device}"

Output::

    {
        "State": "in-use",
        "InstanceId": "i-5203422c",
        "Device": "/dev/sdf"
    }

**Example 7: To create a snapshot of the volume**

The following ``create-snapshot`` example creates a snapshot of the attached volume with a description. ::

    aws ec2 create-snapshot \
        --volume-id vol-1234567890abcdef0 \
        --description "Snapshot of MyDataVolume"

Output::

    {
        "Description": "Snapshot of MyDataVolume",
        "Tags": [],
        "Encrypted": false,
        "VolumeId": "vol-1234567890abcdef0",
        "State": "pending",
        "VolumeSize": 20,
        "StartTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "Progress": "",
        "OwnerId": "123456789012",
        "SnapshotId": "snap-066877671789bd71b"
    }

**Example 8: To wait until the snapshot is completed**

The following ``wait snapshot-completed`` example pauses until the snapshot finishes. It produces no output. ::

    aws ec2 wait snapshot-completed \
        --snapshot-ids snap-066877671789bd71b

**Example 9: To detach the volume from the instance**

The following ``detach-volume`` example detaches the volume from the instance. ::

    aws ec2 detach-volume \
        --volume-id vol-1234567890abcdef0

Output::

    {
        "AttachTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "InstanceId": "i-5203422c",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "detaching",
        "Device": "/dev/sdf"
    }

**Example 10: To wait until the volume is available again**

The following ``wait volume-available`` example pauses until the volume is fully detached and available. It produces no output. ::

    aws ec2 wait volume-available \
        --volume-ids vol-1234567890abcdef0

**Example 11: To delete the volume**

The following ``delete-volume`` example deletes the volume. If the command succeeds, no output is returned. ::

    aws ec2 delete-volume \
        --volume-id vol-1234567890abcdef0

**Example 12: To terminate the instance**

The following ``terminate-instances`` example terminates the instance used in this workflow. ::

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
                    "Code": 16,
                    "Name": "running"
                }
            }
        ]
    }
