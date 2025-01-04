import boto3
# Initialize SQS client
sqs = boto3.client('sqs')

# Create a queue
queue_name = "MSc_Exercise_Queue"
response = sqs.create_queue(QueueName=queue_name)
queue_url = response['QueueUrl']
print(f"Queue created: {queue_url}")

# Send messages
for i in range(1, 6):
    message = f"Message {i}"
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)

# Receive messages
response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=5)
messages = response.get('Messages', [])
for message in messages:
    print(f"Received: {message['Body']}")
    # Delete the message
    sqs.delete_message(QueueUrl=queue_url,
ReceiptHandle=message['ReceiptHandle'])
