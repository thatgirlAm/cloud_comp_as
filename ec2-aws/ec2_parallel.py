import paramiko
from threading import Thread


def upload_file_to_instance(host, key_file, username, local_path, remote_path):
    """
    Uploads a file to an EC2 instance via SFTP.

    Args:
        host (str): The public IP of the instance.
        key_file (str): Path to the private key file.
        username (str): SSH username for the EC2 instance.
        local_path (str): Local file to upload.
        remote_path (str): Destination path on the instance.
    """
    try:
        print(f"Uploading {local_path} to {host}:{remote_path}...")
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, pkey=paramiko.RSAKey.from_private_key_file(key_file))
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()
        print(f"Successfully uploaded {local_path} to {host}:{remote_path}")
    except Exception as e:
        print(f"Failed to upload file to {host}: {e}")


def execute_word_count_on_instance(host, key_file, username, chunk_path):
    """
    Executes the word_counter function on a remote EC2 instance.

    Args:
        host (str): The public IP address of the instance.
        key_file (str): Path to the private key file.
        username (str): SSH username for the EC2 instance.
        chunk_path (str): Path to the chunk file on the EC2 instance.
    """
    try:
        print(f"Connecting to {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, key_filename=key_file)

        # Properly format the inline Python code
        command = f"""
        python3 -c '
def word_counter(file_path):
    with open(file_path, "r") as file:
        count = sum(len(line.split()) for line in file)
    print(f"({host}, {{count}})")

word_counter("{chunk_path}")
'
        """
        print(f"Executing word_counter on {host} for {chunk_path}...")
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read the outputs
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Output from {host}:\n{output}")
        if error:
            print(f"Error from {host}:\n{error}")

        ssh.close()
    except Exception as e:
        print(f"Failed to execute command on {host}: {e}")

def run_word_count_parallel(instance_details):
    """
    Executes the word_counter function on multiple EC2 instances in parallel.

    Args:
        instance_details (list of tuples): Each tuple contains (public_ip, local_chunk_path, remote_chunk_path).
    """
    threads = []
    key_file = "C:/Users/amaelle.diop/Downloads/labsuser (2).pem"  # Path to your private key file
    username = "ec2-user"  # Replace with your EC2 username

    for public_ip, local_chunk_path, remote_chunk_path in instance_details:
        # Upload chunk file to the instance
        upload_file_to_instance(public_ip, key_file, username, local_chunk_path, remote_chunk_path)

        # Execute the word_counter function on the instance
        thread = Thread(target=execute_word_count_on_instance, args=(public_ip, key_file, username, remote_chunk_path))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

'''
def main():
    # Instance details: (public_ip, local_chunk_path, remote_chunk_path)
    instance_details = [
        ("54.160.147.198", "C:/Users/amaelle.diop/Downloads/chunk1.txt", "/home/ec2-user/chunk1.txt"),
        ("54.224.5.167", "C:/Users/amaelle.diop/Downloads/chunk2.txt", "/home/ec2-user/chunk2.txt"),
        ("54.208.8.55", )
    ]

    # Run the word counter in parallel on multiple EC2 instances
    run_word_count_parallel(instance_details)


if __name__ == "__main__":
    main()
'''