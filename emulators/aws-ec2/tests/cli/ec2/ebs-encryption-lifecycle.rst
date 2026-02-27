**Example 1: To check EBS encryption status before making changes**

The following ``get-ebs-encryption-by-default`` example checks whether EBS encryption by default is enabled. ::

    aws ec2 get-ebs-encryption-by-default

Output::

    {
        "EbsEncryptionByDefault": false
    }

**Example 2: To enable EBS encryption by default**

The following ``enable-ebs-encryption-by-default`` example enables EBS encryption by default for your AWS account in the current Region. ::

    aws ec2 enable-ebs-encryption-by-default

Output::

    {
        "EbsEncryptionByDefault": true
    }

**Example 3: To verify EBS encryption is enabled**

The following ``get-ebs-encryption-by-default`` example verifies that EBS encryption by default is now enabled. ::

    aws ec2 get-ebs-encryption-by-default

Output::

    {
        "EbsEncryptionByDefault": true
    }

**Example 4: To disable EBS encryption by default**

The following ``disable-ebs-encryption-by-default`` example disables EBS encryption by default for your AWS account in the current Region. ::

    aws ec2 disable-ebs-encryption-by-default

Output::

    {
        "EbsEncryptionByDefault": false
    }

**Example 5: To verify EBS encryption is disabled**

The following ``get-ebs-encryption-by-default`` example verifies that EBS encryption by default is now disabled. ::

    aws ec2 get-ebs-encryption-by-default

Output::

    {
        "EbsEncryptionByDefault": false
    }
