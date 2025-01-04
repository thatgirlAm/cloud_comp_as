#--------------------Cloud Computing Assignment--------------------#
#-------------------Amaëlle T. M. DIOP - 461543-------------------#


#--------------------Imports--------------------#
import boto3
from botocore.exceptions import ClientError
import os
import processing
import ec2_parallel  # Ensure you have this module imported for parallel execution

#--------------------globals--------------------#
RESPONSE = None
MAX_SIZE = 5 * 1024 * 1024
FILE_PATH = "C:/Users/amaelle.diop/OneDrive - ESTIA/Documents/ec2-aws/_file.txt"
REPOSITORY = "C:/Users/amaelle.diop/OneDrive - ESTIA/Documents/ec2-aws/"

#--S3 storage--#
BUCKET_NAME = "bucck-words-2"
S3_KEY = "file.txt"
S3 = boto3.client('s3')

#--QUEUEING--#
QUEUE_NAME = "word_count_1"
sqs = boto3.client('sqs')
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/881465423296/word_count_1"
MAX_WAITING_TIME = 20
MAX_MESSAGES = 10

#--Processing--#
CHUNK_PATH = "C:/Users/amaelle.diop/Downloads/chunk"

# Instance details
INSTANCE_MAP = {
    0: "54.208.8.55",
    1: "54.224.5.167",
    2: "54.160.147.198"
}


#--------------------Functions--------------------#

def upload_file(file_path, bucket_name, s3_key):
    global RESPONSE
    try:
        S3.upload_file(file_path, bucket_name, s3_key)
        RESPONSE = "File uploaded successfully"
    except ClientError as e:
        RESPONSE = f"Upload failed: {e}"


def queue(queue_name, chunk_id, instance_id):
    response = sqs.create_queue(QueueName=queue_name)
    queue_url = response['QueueUrl']
    message = f"({instance_id}, {chunk_id})"
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def purge_messages(queue_url):
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
        messages = response.get('Messages', [])
        if not messages:
            break
        for message in messages:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])


def main(file_path, max_size):
    # Purge any existing messages in the queue
    purge_messages(QUEUE_URL)
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")

    # Initialize variables
    instance_number = 0
    details = []
    part_number = 1

    with open(file_path, 'rb') as f:
        chunk = f.read(max_size)

        while chunk:
            # Save the chunk locally
            local_chunk_path = f"{REPOSITORY}part_{part_number}.txt"
            with open(local_chunk_path, 'wb') as part_file:
                part_file.write(chunk)

            # Upload the chunk to S3
            s3_key = f"chunk_{part_number}.txt"
            upload_file(local_chunk_path, BUCKET_NAME, s3_key)
            print(f"Uploaded {s3_key}")

            # Assign the chunk to an instance
            instance_id = instance_number % len(INSTANCE_MAP)
            processing.INPUT_MESSAGES.append((part_number, instance_id))

            # Prepare instance details
            remote_chunk_path = f"/home/ec2-user/{s3_key}"
            details.append((INSTANCE_MAP[instance_id], local_chunk_path, remote_chunk_path))

            # Update counters and read the next chunk
            instance_number += 1
            part_number += 1
            chunk = f.read(max_size)

    # Run the word counter on all instances in parallel
    ec2_parallel.run_word_count_parallel(details)
    print("Processing completed successfully!")


if __name__ == "__main__":
    main(FILE_PATH, MAX_SIZE)
    print(RESPONSE)
