#--------------------Cloud Computing Assignment--------------------#
#-------------------Amaëlle T. M. DIOP - 461543-------------------#


#--------------------Imports--------------------#
import boto3
from botocore.exceptions import ClientError
import os
import processing

#--------------------globals--------------------#
RESPONSE  = None
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


#--------------------Functions--------------------#

#--------------------Upload function : uploading a file to an s3 bucket--------------------#
def upload_file(file_path, bucket_name, s3_key):
    global RESPONSE
    try :
        S3.upload_file(file_path, bucket_name, s3_key)
        RESPONSE = "File uploaded successfully"
    except ClientError as e:
            RESPONSE = (f"Upload failed: {e}")

#--------------------Queue function : queueing a file's info in an SQS queue--------------------#
def queue(queue_name, chunk_id, instance_id):
    response = sqs.create_queue(QueueName=queue_name)
    queue_url = response['QueueUrl']
    message = f"({instance_id}, {chunk_id})"
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)

#--------------------Purge function : purging a whole queue from messages--------------------#
def purge_messages(queue_url):
    while True:
        # Receive a batch of messages
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
        messages = response.get('Messages', [])
        if not messages:
            break
        for message in messages:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])


#--------------------Main function : splitting the file every 5MB--------------------#
#-----------In this function, the text file is split, uploaded to the bucket and queued-----------#
def main(file_path, max_size):
    purge_messages(QUEUE_URL)
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    instance_number = 0

    with open(file_path, 'rb') as f:
        chunk = f.read(max_size)
        part_number = 1

        while chunk:
            #--------------------Processing each chunk--------------------#
            with open(f"part_{part_number}.txt", 'wb') as part_file:
                part_file.write(chunk)
                upload_file(REPOSITORY + f"part_{part_number}.txt", BUCKET_NAME, f"chunk_{part_number}.txt")
                processing.INPUT_MESSAGES+=[(part_number, instance_number)]
            print(f"Uploaded chunk{part_number}.txt")
            instance_number+=1
            if instance_number>2:
                instance_number = 0
            part_number += 1
            chunk = f.read(max_size)  #---next chunk---#
            processing.print_messages(QUEUE_URL, MAX_MESSAGES, MAX_WAITING_TIME)

            '''
    for i in range(len(processing.INPUT_MESSAGES)):
        print(processing.INPUT_MESSAGES[i])'''
    processing.queue_chunks_to_instances(BUCKET_NAME, QUEUE_URL)


main(FILE_PATH, MAX_SIZE)
print(RESPONSE)
