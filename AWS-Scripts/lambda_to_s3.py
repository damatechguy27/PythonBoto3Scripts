import boto3
import json
import time
from datetime import datetime, timedelta

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
    parameter_name = f'/log-export-checkpoints/{log_group_name}'
    try:
        response = ssm.get_parameter(Name=parameter_name)
        timestamp_str = response['Parameter']['Value']
        return int(timestamp_str)
    except ssm.exceptions.ParameterNotFound:
        return 0

def set_last_export_timestamp(log_group_name, timestamp):
    parameter_name = f'/log-export-checkpoints/{log_group_name}'
    timestamp_str = str(timestamp)
    ssm.put_parameter(Name=parameter_name, Value=timestamp_str, Type='String', Overwrite=True)

def lambda_handler(event, context):
    # Get current timestamp
    current_timestamp = int(time.time())

    # Get all log groups
    log_groups = get_all_log_groups()

    for log_group in log_groups:
        log_group_name = log_group['logGroupName']

        if should_exclude(log_group_name):
            continue  # Skip excluded log groups

        # Get last export timestamp from SSM
        last_export_timestamp = get_last_export_timestamp(log_group_name)

        # Check if 24 hours have passed since the last export
        if current_timestamp - last_export_timestamp < 24 * 3600:
            print(f"Skipping export for log group '{log_group_name}' as 24 hours have not passed.")
            continue

        # Set S3 prefix based on log group name
        s3_prefix = f'{log_group_name}/'

        # Create export task
        response = logs.create_export_task(
            logGroupName=log_group_name,
            fromTime=last_export_timestamp * 1000,  # Convert to milliseconds
            to=current_timestamp * 1000,  # Convert to milliseconds
            destination='your-s3-bucket-name',
            destinationPrefix=s3_prefix
        )

        export_task_id = response['taskId']
        print(f"Export task created for log group '{log_group_name}'. Task ID: {export_task_id}")

        # Update last export timestamp in SSM
        set_last_export_timestamp(log_group_name, current_timestamp)

    return {
        'statusCode': 200,
        'body': 'CloudWatch Logs export tasks created'
    }
