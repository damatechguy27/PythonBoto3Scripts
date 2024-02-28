import csv
import boto3
from configparser import ConfigParser
from botocore.session import Session

def add_security_group_rule(security_group_id, ip_protocol, from_port, to_port, cidr_ip, description):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': ip_protocol,
                    'FromPort': from_port,
                    'ToPort': to_port,
                    'IpRanges': [
                        {
                            'CidrIp': cidr_ip,
                            'Description': description
                        },
                    ],
                },
            ],
        )
        print("Rule added successfully: ", response)
    except Exception as e:
        print("Error adding rule: ", str(e))

def main():

    # Read AWS credentials file
    config = ConfigParser()
    #config.read('C:\\Users\\dmit27\\.aws\\credentials')  # Update with the correct path if needed
    config.read('<path to your .aws/credentials file>')
    # grabs the results 
    # Get the list of profile names
    profiles = config.sections()

    account_name = '<enter your profile name here>'

    # Iterate through each profile
    for profile in profiles:

        session = Session(profile=profile)

        credentials = session.get_credentials()

        region = '<enter region here>'

        sesh = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=region
        )

        if profile == account_name:
        # Printing All Profiles in creds file 
            print(f"Processing profile: {account_name}")
        
            # Set the name of the security group
            security_group_name = '<enter security group name>'

            # Read CSV file with rules data make sure the csv is in the same directory as the script
            with open('sg_rules.csv', mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Extract rule information from CSV
                    ip_protocol = row['Protocol']
                    from_port = int(row['From Port'])
                    to_port = int(row['To Port'])
                    cidr_ip = row['Source IP']
                    description = row['Description']

                    # Get security group ID by name  
                    ec2 = sesh.client('ec2')
                    response = ec2.describe_security_groups(
                        Filters=[
                            {'Name': 'group-name', 'Values': [security_group_name]}
                        ]
                    )
                    security_group_id = response['SecurityGroups'][0]['GroupId']

                    # Add rule to the security group
                    add_security_group_rule(security_group_id, ip_protocol, from_port, to_port, cidr_ip, description)

if __name__ == "__main__":
    main()
