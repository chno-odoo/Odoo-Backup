# A script to automatically take backups of the system and upload it to google drive as long as rclone is configured properly #
# Written by chno
# Created on: Fri Oct  4 01:06:56 PM EDT 2024
# Last Updated: Mon Oct  7 03:06:48 PM EDT 2024
# Last update: Fixed max number of retires as well as added additional error handling. 

### Imports ###
import os
import subprocess
from datetime import datetime
import time

### Paths and configurations ###
BACKUP_DIR = "/home/odoo"  # Backup home directory
BACKUP_NAME = f"backup-{datetime.now().strftime('%Y-%m-%d')}.tar.gz"
BACKUP_PATH = f"/tmp/{BACKUP_NAME}"
LOG_FILE = f"/tmp/backup_log_{datetime.now().strftime('%Y-%m-%d')}.log"

### Functions ###

def log_message(message):
    """Log a message to the console and to the log file."""
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

def create_backup():
    log_message(f"Creating backup: {BACKUP_NAME}")

    try:
        # Exclude dynamically changing files like browser cache
        exclude_paths = [
            '--exclude=/home/odoo/.cache',
            '--exclude=/home/odoo/.config/discord',
            '--exclude=/home/odoo/.mozilla',
            '--exclude=/home/odoo/.google-chrome'
        ]

        # Add the exclude paths to the tar command
        tar_command = ["tar", "-czvf", BACKUP_PATH] + exclude_paths + [BACKUP_DIR, "--ignore-failed-read"]

        # Run the tar command and capture both stdout and stderr
        result = subprocess.run(
            tar_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        # Log the tar output (list of backed-up files)
        log_message(result.stdout)

        # Filter and display ignored files based on permission issues
        ignored_files = [line for line in result.stderr.split('\n') if 'Cannot open' in line]
        if ignored_files:
            log_message("\nThe following files were ignored due to permission issues:")
            for file in ignored_files:
                log_message(file)

        log_message("Backup process completed successfully.")

    except subprocess.CalledProcessError as e:
        # Catch the CalledProcessError and handle it
        log_message(f"Backup process failed with error:\n{e.stderr}")
        
        # Display ignored files or errors encountered
        ignored_files = [line for line in e.stderr.split('\n') if 'Cannot open' in line]
        if ignored_files:
            log_message("\nThe following files were ignored due to permission issues:")
            for file in ignored_files:
                log_message(file)

        log_message("Backup process encountered issues, but some files may still have been backed up.")
    
    except Exception as e:
        # Catch any other unforeseen errors
        log_message(f"An unexpected error occurred: {str(e)}")
        raise

def upload_to_google_drive():
    log_message("Uploading backup to Google Drive...")

    max_retries = 3
    attempt = 0
    error_message = None  # Initialize error_message in case retries are exhausted

    while attempt < max_retries:
        try:
            # Upload backup to Google Drive using rclone
            subprocess.run(["rclone", "copy", BACKUP_PATH, "gdrive:/backups/"], check=True)
            log_message("Backup uploaded to Google Drive successfully.")
            return  # Exit the function after a successful upload
    
        except subprocess.CalledProcessError as e:
            log_message(f"Failed to upload backup to Google Drive. Error: {e.stderr}")
            error_message = str(e.stderr)  # Assign the last error message
            
            if "rateLimitExceeded" in e.stderr:
                attempt += 1
                log_message(f"Rate limit exceeded. Retrying {attempt}/{max_retries}...")
                time.sleep(60)  # Wait for 60 seconds before retrying
            else:
                raise  # Raise the exception if necessary for further handling

    log_message(f"Failed to upload backup after multiple tries. Last error: {error_message}")

def clean_up():
    # Function to clean up the backup directory from the local machine #
    try:
        if os.path.exists(BACKUP_PATH):
            os.remove(BACKUP_PATH)
            log_message(f"Cleaned up local backup: {BACKUP_NAME}")
    except Exception as e:
        log_message(f"Error during cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    try: 
        create_backup()
        upload_to_google_drive()
    finally:
        clean_up()
