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

**Example 3: To tag the instance**

The following ``create-tags`` example tags the instance with ``Name=MyInstance``. ::

    aws ec2 create-tags \
        --resources i-5203422c \
        --tags Key=Name,Value=MyInstance

**Example 4: To filter instances by tag and find no match**

The following ``describe-instances`` example filters by a tag that does not match any existing instance, returning an empty result. ::

    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=NonExistentInstance"

Output::

    {
        "Reservations": []
    }

**Example 5: To terminate the instance**

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

For more information, see `Launching, listing, and deleting Amazon EC2 instances in the AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-services-ec2-instances.html>`
