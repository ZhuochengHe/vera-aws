**Example 1: To launch an instance**

The following ``run-instances`` example launches a ``t2.micro`` instance. ::

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

**Example 2: To wait until the instance is running**

The following ``wait instance-running`` example pauses until the instance is running. It produces no output. ::

    aws ec2 wait instance-running \
        --instance-ids i-5203422c

**Example 3: To query the instance ID**

The following ``describe-instances`` example filters by instance type and returns only the instance ID. ::

    aws ec2 describe-instances \
        --filters "Name=instance-type,Values=t2.micro" \
        --query "Reservations[].Instances[].InstanceId"

Output::

    [
        "i-5203422c"
    ]

**Example 4: To query the current state of the instance**

The following ``describe-instances`` example filters by instance type and returns only the current state of the instance. ::

    aws ec2 describe-instances \
        --filters "Name=instance-type,Values=t2.micro" \
        --query "Reservations[].Instances[].State"

Output::

    [
        {
            "Code": 16,
            "Name": "running"
        }
    ]

**Example 5: To query the instance ID and current state together**

The following ``describe-instances`` example filters by instance type and returns the instance ID alongside its current state. ::

    aws ec2 describe-instances \
        --filters "Name=instance-type,Values=t2.micro" \
        --query "Reservations[].Instances[].{InstanceId:InstanceId,State:State.Name}"

Output::

    [
        {
            "InstanceId": "i-5203422c",
            "State": "running"
        }
    ]

**Example 6: To terminate the instance**

The following ``terminate-instances`` example terminates the instance. ::

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

**Example 7: To wait until the instance is terminated**

The following ``wait instance-terminated`` example pauses until the instance is terminated. It produces no output. ::

    aws ec2 wait instance-terminated \
        --instance-ids i-5203422c

