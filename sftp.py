import os
import paramiko
import csv
import socket
import logging
from dotenv import load_dotenv

MAX_RETRIES = 3

dotenv_path = ".env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def validate_private_key(private_key_path):
    """
    Validates the private key file.

    Parameters:
    - private_key_path (str): Path to the private key file.

    Returns:
    - bool: True if the private key is valid, False otherwise.
    """
    try:
        private_key = paramiko.RSAKey(filename=private_key_path)
        return True
    except paramiko.ssh_exception.SSHException:
        return False

def is_host_reachable(host, port=22):
    """
    Checks if the specified host is reachable.

    Parameters:
    - host (str): Hostname or IP address.
    - port (int): Port number (default is 22).

    Returns:
    - bool: True if the host is reachable, False otherwise.
    """
    try:
        socket.create_connection((host, port), timeout=10)
        return True
    except (ConnectionRefusedError, socket.gaierror):
        return False

def setup_logging(log_level):
    """
    Configures logging to the console with the INFO level.
    """
    logging.basicConfig(level=log_level)

def sftp_transfer(host, port, username, private_key_path, file_list_path):
    """
    Performs SFTP file transfer to the specified host.

    Parameters:
    - host (str): Hostname or IP address.
    - port (int): Port number.
    - username (str): Username for authentication.
    - private_key_path (str): Path to the private key file for authentication.
    - file_list_path (str): Path to the file containing the list of files to transfer.
    """
    if not validate_private_key(private_key_path):
        logging.error("Invalid private key.")
        return

    if not is_host_reachable(host, port):
        logging.error("Host is not reachable.")
        return

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(host, port=port, username=username, key_filename=private_key_path)
    except paramiko.ssh_exception.AuthenticationException:
        logging.error("Authentication error.")
        return
    except paramiko.ssh_exception.SSHException:
        logging.error("SSH error.")
        return
    except Exception as e:
        logging.error(f"Error connecting via SSH: {e}")
        return

    sftp = ssh_client.open_sftp()

    with open(file_list_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            source = row['Source']
            destination = row['Destination']
            retry_count = 0
            logging.info(f"CSV read file {source} to {destination}")

            while retry_count < MAX_RETRIES:
                try:
                    sftp.get(source, destination)
                    logging.info(f"File {source} transferred to {destination}")
                    break
                except FileNotFoundError as e:
                    logging.error(f"File not found: {e}")
                except PermissionError as e:
                    logging.error(f"Permission error: {e}")
                except IOError as e:
                    logging.error(f"I/O error: {e}")
                except Exception as e:
                    logging.error(f"Error transferring file {source}: {e}")
                retry_count += 1
                
            if retry_count == MAX_RETRIES:
                logging.error(f"The file {source} failed after {MAX_RETRIES} retries.")

    sftp.close()
    ssh_client.close()

if __name__ == "__main__":
    required_env_variables = ["SFTP_HOST", "SFTP_USERNAME", "SFTP_PRIVATE_KEY_PATH", "SFTP_FILE_LIST_PATH"]

    # Check if all required environment variables are set
    missing_variables = [var for var in required_env_variables if not os.getenv(var)]

    if missing_variables:
        error_message = f"Missing required environment variables: {', '.join(missing_variables)}"
        logging.error(error_message)
        raise ValueError(error_message)
    
    host = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USERNAME")
    private_key_path = os.getenv("SFTP_PRIVATE_KEY_PATH")
    file_list_path = os.getenv("SFTP_FILE_LIST_PATH")
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

    setup_logging(log_level)

    try:
        sftp_transfer(host, port, username, private_key_path, file_list_path)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"Global SFTP error: {e}")
