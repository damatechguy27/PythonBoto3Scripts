import boto3
import json

s3 = boto3.client('s3')
logs = boto3.client('logs')

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

def lambda_handler(event, context):
    # Get all log groups
    log_groups = get_all_log_groups()

    for log_group in log_groups:
        log_group_name = log_group['logGroupName']

        if should_exclude(log_group_name):
            continue  # Skip excluded log groups

        # Set S3 prefix based on log group name
        s3_prefix = f'{log_group_name}/'

        # Create export task
        response = logs.create_export_task(
            logGroupName=log_group_name,
            fromTime=0,
            to=9999999999999,
            destination='your-s3-bucket-name',
            destinationPrefix=s3_prefix
        )

        export_task_id = response['taskId']
        print(f"Export task created for log group '{log_group_name}'. Task ID: {export_task_id}")

    return {
        'statusCode': 200,
        'body': 'CloudWatch Logs export tasks created'
    }
