import boto3
import time
import subprocess
import json
from botocore.exceptions import ClientError



SQS = boto3.client('sqs')
S3 = boto3.client('s3')
EC2 = boto3.client('ec2')
RESULTS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/881465423296/results_queue"
LOCAL_FILE_PATH = "C:/Users/amaelle.diop/Downloads/"
REPOSITORY = "C:/Users/amaelle.diop/OneDrive - ESTIA/Documents/ec2-aws/"

#--Processing--#
INPUT_MESSAGES = []

#--ec2 instances--#
RESPONSE = EC2.describe_instances()

def print_messages(queue_url, max_messages, wait_time):
    while True:
        try:
            #----Receive a batch of messages----#
            response = SQS.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_messages,
                                           WaitTimeSeconds=wait_time)
            messages = response.get('Messages', [])
            if not messages:
                break

            #----Process each message----#
            for message in messages:
                print(message['Body'])
                #process_message(message)
                #--Deleting messages from the queue after processing--#
                #SQS.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

        except Exception as e:
            print(f"Error while printing messages: {e}")
            time.sleep(10)

'''
def process_message(message):
    global INPUT_MESSAGES
    INPUT_MESSAGES+=[(int(message['Body'][1]),int(message['Body'][4]))]
'''

#--List objects in S3 bucket--#
def list_chunks_in_bucket(bucket_name, prefix=''):
    response = S3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    objects = response.get('Contents', [])
    return [obj['Key'] for obj in objects]


'''
#--Queue chunks to SQS--#
def queue_chunks_to_instances(bucket_name, queue_url, instances, prefix=''):
    chunks = list_chunks_in_bucket(bucket_name, prefix)
    instance_count = len(instances)
    instance_index = 0

    for chunk in chunks:
        #--Assign chunk to an instance--#
        instance_id = instances[instance_index]
        message = f"{instance_id}:{chunk}"
        SQS.send_message(QueueUrl=queue_url, MessageBody=message)
        print(f"Queued {chunk} to instance {instance_id}")

        #--Update instance index--#
        instance_index = (instance_index + 1) % instance_count

def queue_chunks_based_on_input_messages(bucket_name, queue_url, prefix=''):
    #--List all chunks in the S3 bucket--#
    chunks = list_chunks_in_bucket(bucket_name, prefix)
    chunk_map = {int(chunk.split('.')[0][5:]): chunk for chunk in chunks}  # Map chunk_id to S3 key

    for chunk_id, instance_id in INPUT_MESSAGES:
        #--Match chunk_id to the S3 key--#
        chunk_key = chunk_map.get(chunk_id)
        if not chunk_key:
            print(f"Chunk {chunk_id} not found in S3 bucket.")
            continue

        #--Create the message and send to the queue--#
        message = f"{instance_id}:{chunk_key}"
        SQS.send_message(QueueUrl=queue_url, MessageBody=message)
        print(f"Queued chunk {chunk_key} to instance {instance_id}")
'''

def queue_chunks_to_instances(bucket_name, queue_url):
    for chunk_id, instance_id in INPUT_MESSAGES:
        chunk_key = f"chunk{chunk_id}.txt"
        message = f"{instance_id},{chunk_id},{chunk_key}"
        SQS.send_message(QueueUrl=queue_url, MessageBody=message)
        print(f"Queued chunk {chunk_id} for instance {instance_id}")
        process_instance_message(queue_url, instance_id, bucket_name)


def process_instance_message(queue_url, instance_id, bucket_name):
    while True:
        response = SQS.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=20)
        messages = response.get('Messages', [])

        if not messages:
            break
        for message in messages:
            body = message['Body']
            instance, chunk_id, chunk_key = body.split(',')

            if int(instance) != instance_id:
                continue  #--Skip messages not for this instance--#

            print(f"Processing chunk {chunk_key} for instance {instance_id}")  # Added logging

            #--Download the chunk from S3--#
            try:
                S3.download_file(bucket_name, chunk_key, LOCAL_FILE_PATH+chunk_key)
            except ClientError as e:
                print(f"Error downloading chunk {chunk_key}: {e}")
                continue  # Proceed to the next chunk
