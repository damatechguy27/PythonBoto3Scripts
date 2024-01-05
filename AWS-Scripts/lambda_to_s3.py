import boto3
import json
import os
import time

s3 = boto3.client('s3')
logs = boto3.client('logs')
ssm = boto3.client('ssm')

exclusion_list = ['excluded-log-group-1', 'excluded-log-group-2']  # Add log groups to exclude

def should_exclude(log_group_name):
    return log_group_name in exclusion_list

def get_all_log_groups():
    log_groups = []
    next_token = None

    while True:
        if next_token:
            response = logs.describe_log_groups(nextToken=next_token)
        else:
            response = logs.describe_log_groups()

        log_groups.extend(response['logGroups'])
        next_token = response.get('nextToken')

        if not next_token:
            break

    return log_groups

def get_last_export_timestamp(log_group_name):
    ssm_parameter_name = ("/log-exporter-last-export/%s" % log_group_name).replace("//", "/")

    try:
        ssm_response = ssm.get_parameter(Name=ssm_parameter_name)
        return int(ssm_response['Parameter']['Value'])
    except ssm.exceptions.ParameterNotFound:
        return 0

def set_last_export_timestamp(log_group_name, timestamp):
    ssm_parameter_name = ("/log-exporter-last-export/%s" % log_group_name).replace("//", "/")

    ssm.put_parameter(
        Name=ssm_parameter_name,
        Value=str(timestamp),
        Type='String',
        Overwrite=True
    )

def lambda_handler(event, context):
    # Get the S3 bucket name from environment variable
    s3_bucket_name = os.environ['S3_BUCKET']

    # Get all log groups
    log_groups = get_all_log_groups()

    for log_group in log_groups:
        log_group_name = log_group['logGroupName']

        if should_exclude(log_group_name):
            continue  # Skip excluded log groups

        # Get the last export timestamp from SSM Parameter Store
        last_export_timestamp = get_last_export_timestamp(log_group_name)

        # Get the current timestamp
        current_timestamp = int(round(time.time() * 1000))

        print(f"--> Exporting {log_group_name} to {s3_bucket_name}")

        if current_timestamp - last_export_timestamp < (24 * 60 * 60 * 1000):
            # Skip export if less than 24 hours since the last export
            print("    Skipped until 24hrs from last export is completed")
            continue

        # Set the last export timestamp to the current time
        set_last_export_timestamp(log_group_name, current_timestamp)

        # Set S3 prefix based on log group name
        s3_prefix = f'{log_group_name}/'

        # Create export task
        response = logs.create_export_task(
            logGroupName=log_group_name,
            fromTime=0,
            to=9999999999999,
            destination=s3_bucket_name,
            destinationPrefix=s3_prefix
        )

        export_task_id = response['taskId']
        print(f"Export task created for log group '{log_group_name}'. Task ID: {export_task_id}")

    return {
        'statusCode': 200,
        'body': 'CloudWatch Logs export tasks created'
    }
