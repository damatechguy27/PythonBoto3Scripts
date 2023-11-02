def lambda_handler(event, context):
    import boto3
    import csv
    from datetime import date
    import os

    # specifying which module I am using 
    ec2_cli = boto3.client('ec2', region_name="us-west-2")
    s3 = boto3.client('s3')

    #getting attributes name 
    file_name = "allec2-tags-" + str(date.today()) + ".csv"
    file_path = "/tmp/allec2-tags-" + str(date.today()) + ".csv"
    bucket_name = 'testscript-dam'

    # Get a list of all EC2 instances
    response = ec2_cli.describe_instances()
    instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]

    # Collect all unique tag keys
    tag_keys = set()
    for instance in instances:
        tags = instance.get('Tags', [])
        for tag in tags:
            tag_keys.add(tag['Key'])

    # Write tags to a CSV file
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['Instance_ID', 'Instance_Type', 'Status'] + list(tag_keys)  # Include 'Instance ID' as the first column
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for instance in instances:
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            tags['Instance_ID'] = instance['InstanceId']
            tags['Instance_Type'] = instance['InstanceType']
            tags['Status'] = instance['State'] ['Name']
            writer.writerow(tags)

    #uploading to s3
    s3.upload_file(file_path, bucket_name, file_name)

    #removing file out of temp dictionary
    os.remove(file_path)

    return {
                'statusCode': 200,
                'body': 'EC2 instance statuses retrieved, printed to CSV, and uploaded to S3.'
            } 