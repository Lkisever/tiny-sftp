# Tiny Secure File Transfer Utility

This utility provides a simple command-line interface to transfer files using SFTP (Secure File Transfer Protocol). It is designed to be lightweight and easy to use, with support for key-based authentication and automatic retries for failed transfers.

## Features

- Key-based authentication using private keys.
- Host reachability check before attempting file transfer.
- Configurable logging levels.
- Automatic retries for transient errors during file transfer.
- Environment variable configuration for easy deployment.

## Prerequisites

To use this utility, you will need:

- Python 3.8 or higher.
- Paramiko library (installed automatically with requirements).
- Access to an SFTP server with your public key added for authentication.

## Setup

1. Clone the repository or download the source code.
2. Install the required Python dependencies by running `pip install -r requirements.txt`.
3. Set up the required environment variables or use a `.env` file for configuration.

## Configuration

The utility can be configured using the following environment variables:

- `SFTP_HOST`: The hostname or IP address of the SFTP server.
- `SFTP_PORT`: The port number of the SFTP server (default is 22).
- `SFTP_USERNAME`: The username for SFTP authentication.
- `SFTP_PRIVATE_KEY_PATH`: The path to the private key file for SFTP authentication.
- `SFTP_FILE_LIST_PATH`: The path to the file containing the list of files to transfer.
- `LOG_LEVEL`: The logging level (e.g., INFO, ERROR, DEBUG).
- `PREFERRED_KEY_ALGORITHM` : Public key algorithms supported by the client if provided

## Usage

To run the SFTP file transfer utility, you can execute it directly with Python or use the provided Docker container. Here are the commands for both methods:

Direct execution:
```bash
python sftp.py
```

Ensure that the environment variables are set before running the script, or that a `.env` file is present in the working directory.

Docker execution:
```bash
# Build the Docker image
docker build -t tiny-sftp .

# Run the Docker container
# Mount the /data/ directory to access the private key and the file list
docker run --env-file .env -v /path/to/data:/data tiny-sftp
```

Make sure to replace `/path/to/data` with the actual path to your data directory containing the private key and the file list.

Here is an example of what your `.env` file should look like:

```
SFTP_HOST=sftp.example.com
SFTP_PORT=22
SFTP_USERNAME=user
SFTP_PRIVATE_KEY_PATH=/data/private_key.pem
SFTP_FILE_LIST_PATH=/data/list.txt
LOG_LEVEL=INFO
```

Replace the values with your actual SFTP server details and file paths.

```bash
# Build the Docker image
docker build -t tiny-sftp .
```

Replace `.env` with the path to your environment file if necessary.

## CSV File Format

The utility requires a CSV file to specify the source and destination paths for the files to be transferred. The CSV file should have two columns: `Source` and `Destination`. Each row represents a file transfer operation, where `Source` is the file path on the SFTP server, and `Destination` is the local file path where the file should be saved.

Here is an example of the CSV file format:

```
Source,Destination
/remote/path/to/source_file.txt,/local/path/to/destination_file.txt
/remote/path/to/another_source_file.txt,/local/path/to/another_destination_file.txt
```

Ensure that the `SFTP_FILE_LIST_PATH` environment variable points to the location of this CSV file.

## Docker Support

The utility also includes a Dockerfile for containerization. To build and run the utility as a Docker container, use the following commands:

Alternatively, you can pull the pre-built image from Docker Hub using the following command:

```bash
docker pull lkis/tiny-sftp
```


```bash
# Build the Docker image
docker build -t tiny-sftp .
```
The Dockerfile has been updated to use Python 3.12-slim as the base image and to copy the necessary files for the SFTP transfer. The CMD and ENTRYPOINT instructions have been set to execute the `sftp.py` script.
Replace `.env` with the path to your environment file if necessary.

## Setting Up Rebex Tiny SFTP Server for Testing with Key-Based Authentication

To test the SFTP file transfer utility you can use the Rebex Tiny SFTP Server. Follow these steps to set up the server with key-based authentication:

1. **Download Rebex Tiny SFTP Server:**
   - Visit the [Rebex Tiny SFTP Server](https://www.rebex.net/tiny-sftp-server/) download page.
   - Download the Rebex Tiny SFTP Server installation package.

2. **Install Rebex Tiny SFTP Server:**
   - Run the downloaded installer to install the Rebex Tiny SFTP Server on your machine.
   - Follow the installation wizard instructions to complete the installation.

3. **Configure Rebex Tiny SFTP Server:**
   - After installation, launch the Rebex Tiny SFTP Server application.
   - Configure the SFTP server settings, including:
     - **Root Path:** Specify the root directory where files will be served.
     - **Authentication:** Enable "Public key authentication" and configure user accounts with associated public keys for authentication.
     - **Port:** Note the port number on which the SFTP server is running (default is 22).

4. **Add User Accounts with Public Keys:**
   - In the Rebex Tiny SFTP Server application, navigate to the "Users" tab.
   - Add user accounts for testing purposes.
   - For each user account, specify the public key associated with that account for key-based authentication.

5. **Start the Rebex Tiny SFTP Server:**
   - Click the "Start" button in the Rebex Tiny SFTP Server application to start the SFTP server.

6. **Update Configuration in Your Python Script:**
   - Ensure that the following environment variables in your Python script (`sftp.py`) are configured based on the Rebex Tiny SFTP Server settings:
     - `SFTP_HOST`: Set this to the hostname or IP address of your machine where Rebex Tiny SFTP Server is running.
     - `SFTP_PORT`: Set this to the port number on which Rebex Tiny SFTP Server is listening.
     - `SFTP_USERNAME`: Use the username configured in the Rebex Tiny SFTP Server for testing.
     - `SFTP_PRIVATE_KEY_PATH`: Set this to the local path of the private key file associated with the user account.

7. **Run Your Python Script:**
   - Execute your SFTP file transfer utility using the command:
     ```bash
     python sftp.py
     ```
   - Ensure that the environment variables are set or that a `.env` file is present with the necessary configuration.

8. **Verify File Transfers:**
   - Confirm that the file transfers work as expected with Rebex Tiny SFTP Server using key-based authentication.


## License

This project is licensed under the MIT License - see the LICENSE file for details.
