**Example 1: To launch the first instance**

The following ``run-instances`` example launches a ``t2.micro`` instance tagged ``MyInstance``. ::

    aws ec2 run-instances \
        --image-id ami-xxxxxxxx \
        --count 1 \
        --instance-type t2.micro \
        --key-name MyKeyPair \
        --security-group-ids sg-903004f8 \
        --subnet-id subnet-6e7f829e

Output::

    {
        "OwnerId": "123456789012",
        "ReservationId": "r-5875ca20",
        "Instances": [
            {
                "InstanceId": "i-5203422c",
                "InstanceType": "t2.micro",
                "State": {
                    "Code": 0,
                    "Name": "pending"
                },
                "VpcId": "vpc-1a2b3c4d",
                "SubnetId": "subnet-6e7f829e"
            }
        ]
    }

**Example 2: To wait until the first instance is running**

The following ``wait instance-running`` example pauses until the first instance is running. It produces no output. ::

    aws ec2 wait instance-running \
        --instance-ids i-5203422c

**Example 3: To tag the first instance**

The following ``create-tags`` example tags the first instance with ``Name=MyInstance``. ::

    aws ec2 create-tags \
        --resources i-5203422c \
        --tags Key=Name,Value=MyInstance

**Example 4: To launch the second instance**

The following ``run-instances`` example launches a second ``t2.micro`` instance tagged ``OtherInstance``. ::

    aws ec2 run-instances \
        --image-id ami-xxxxxxxx \
        --count 1 \
        --instance-type t2.micro \
        --key-name MyKeyPair \
        --security-group-ids sg-903004f8 \
        --subnet-id subnet-6e7f829e

Output::

    {
        "OwnerId": "123456789012",
        "ReservationId": "r-6934db31",
        "Instances": [
            {
                "InstanceId": "i-6304533d",
                "InstanceType": "t2.micro",
                "State": {
                    "Code": 0,
                    "Name": "pending"
                },
                "VpcId": "vpc-1a2b3c4d",
                "SubnetId": "subnet-6e7f829e"
            }
        ]
    }

**Example 5: To wait until the second instance is running**

The following ``wait instance-running`` example pauses until the second instance is running. It produces no output. ::

    aws ec2 wait instance-running \
        --instance-ids i-6304533d

**Example 6: To tag the second instance**

The following ``create-tags`` example tags the second instance with ``Name=OtherInstance``. ::

    aws ec2 create-tags \
        --resources i-6304533d \
        --tags Key=Name,Value=OtherInstance

**Example 7: To filter instances by tag and find a match**

The following ``describe-instances`` example filters by ``Name=MyInstance`` and returns only the matching instance. ::

    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=MyInstance"

Output::

    {
        "Reservations": [
            {
                "OwnerId": "123456789012",
                "ReservationId": "r-5875ca20",
                "Instances": [
                    {
                        "InstanceId": "i-5203422c",
                        "InstanceType": "t2.micro",
                        "State": {
                            "Code": 16,
                            "Name": "running"
                        },
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "MyInstance"
                            }
                        ],
                        "VpcId": "vpc-1a2b3c4d",
                        "SubnetId": "subnet-6e7f829e"
                    }
                ]
            }
        ]
    }

**Example 8: To terminate the instances**

The following ``terminate-instances`` example terminates both instances. ::

    aws ec2 terminate-instances \
        --instance-ids i-5203422c i-6304533d

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
            },
            {
                "InstanceId": "i-6304533d",
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

For more information, see `Launching, listing, and deleting Amazon EC2 instances in the AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-services-ec2-instances.html>`