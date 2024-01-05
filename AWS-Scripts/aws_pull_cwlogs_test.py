import boto3
import gzip
import json
import base64

s3 = boto3.client('s3')
logs = boto3.client('logs')

#add log groups to exclude
exclusion_list = ''   # Add log groups to exclude separate with , example -> ['excluded-log-group-1', 'excluded-log-group-2'] 


#this function takes the variable that user adds the log groups to exclude and checks to see
#if any of the excluded log groups are in the log_group_name
def should_exclude(log_group_name):
    return log_group_name in exclusion_list

def lambda_handler(event, context):
    # Get all log groups
    log_groups = logs.describe_log_groups()['logGroups']
    
    #pulls all log group names 
    for log_group in log_groups:
        log_group_name = log_group['logGroupName']

    # log groups found in the exlusion list are skipped
        if should_exclude(log_group_name):
            continue  # Skip excluded log groups

        # Get the latest log stream for the log group
        log_streams = logs.describe_log_streams(logGroupName=log_group_name, orderBy='LastEventTime', descending=True, limit=1)['logStreams']

        if log_streams:
            latest_log_stream = log_streams[0]
            log_stream_name = latest_log_stream['logStreamName']

            # Start querying the log events
            log_events = logs.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)['events']

            # Set S3 key based on log group and stream names
            s3_key = f'{log_group_name}/{log_stream_name}/{context.aws_request_id}.log'

            # Upload the log data to S3
            s3.put_object(
                Bucket='bucketnamehere',
                Key=s3_key,
                Body=json.dumps(log_events)
            )

    return {
        'statusCode': 200,
        'body': 'CloudWatch Logs exported to S3'
    }
