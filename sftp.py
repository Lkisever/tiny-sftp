import os
import csv
import socket
import logging
from dotenv import load_dotenv
from typing import List

import paramiko

MAX_RETRIES = 3

# Load environment variables from .env file
load_dotenv()

def validate_private_key(private_key_path: str) -> bool:
    """
    Validates the private key file.

    Parameters:
    - private_key_path (str): Path to the private key file.

    Returns:
    - bool: True if the private key is valid, False otherwise.
    """
    try:
        with open(private_key_path, 'r') as key_file:
            paramiko.RSAKey(filename=private_key_path)
            return True
    except (FileNotFoundError, paramiko.ssh_exception.SSHException):
        return False

def is_host_reachable(host: str, port: int = 22) -> bool:
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

def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Configures logging to the console with the specified log level.

    Parameters:
    - log_level (int): Logging level (default is logging.INFO).
    """
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s")

def sftp_transfer(host: str, username: str, private_key_path: str, file_list_path: str, port: int = 22) -> None:
    """
    Performs SFTP file transfer to the specified host.

    Parameters:
    - host (str): Hostname or IP address.
    - port (int): Port number (default is 22).
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

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    private_key = paramiko.RSAKey(filename=private_key_path)
    
    # Force the preferred key algorithm only if the variable is provided
    if preferred_key_algorithm:
        logging.info('preferred_key_algorithm : ' + preferred_key_algorithm)
        private_key.key_algorithm = preferred_key_algorithm

    try:
        ssh.connect(host, port=port, username=username, pkey=private_key)
    except paramiko.AuthenticationException:
        logging.error("Authentication error.")
        return
    except paramiko.SSHException as e:
        logging.error(f"Error connecting via SSH: {e}")
        return

    try:
        with ssh.open_sftp() as sftp:
            with open(file_list_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    source, destination = row['Source'], row['Destination']

                    for retry_count in range(MAX_RETRIES):
                        try:
                            sftp.get(source, destination)
                            logging.info(f"Successfully transferred {source} to {destination}")
                            break
                        except (FileNotFoundError, PermissionError, IOError) as e:
                            logging.error(f"Error transferring file {source}: {e}")
                        except Exception as e:
                            logging.error(f"Unexpected error transferring file {source}: {e}")
        logging.info("SFTP transfer completed successfully.")
    finally:
        ssh.close()

def check_env_variables(required_vars: List[str]) -> None:
    """
    Checks if all required environment variables are set.

    Parameters:
    - required_vars (List[str]): List of required environment variable names.

    Raises:
    - ValueError: If any required variable is missing.
    """
    missing_variables = [var for var in required_vars if not os.getenv(var)]
    if missing_variables:
        error_message = f"Missing required environment variables: {', '.join(missing_variables)}"
        logging.error(error_message)
        raise ValueError(error_message)

if __name__ == "__main__":
    required_env_variables = ["SFTP_HOST", "SFTP_USERNAME", "SFTP_PRIVATE_KEY_PATH", "SFTP_FILE_LIST_PATH"]

    check_env_variables(required_env_variables)

    host = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", 22))
    username = os.getenv("SFTP_USERNAME")
    private_key_path = os.getenv("SFTP_PRIVATE_KEY_PATH")
    file_list_path = os.getenv("SFTP_FILE_LIST_PATH")
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
    preferred_key_algorithm = os.getenv("PREFERRED_KEY_ALGORITHM")


    setup_logging(log_level)

    try:
        sftp_transfer(host, username, private_key_path, file_list_path, port)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"Global SFTP error: {e}")