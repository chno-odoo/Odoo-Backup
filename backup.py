# Script used to create the backup
# Written by CHNO
# Creation Date: Wed Oct  9 10:32:38 AM EDT 2024
# Last Updated: Wed Oct  9 11:01:21 AM EDT 2024
# Last Update: Added .local path to the exclude_paths.

import subprocess
import os
from datetime import datetime

def create_backup(backup_dir, rclone_remote, gdrive_folder, log_callback):
    backup_name = f"backup-{datetime.now().strftime('%Y-%m-%d')}.tar.gz"
    backup_path = f"/tmp/{backup_name}"

    # Define the paths to exclude during the backup
    exclude_paths = [
        '--exclude=/home/odoo/.cache',
        '--exclude=/home/odoo/.config',
        '--exclude=/home/odoo/.mozilla',
        '--exclude=/home/odoo/.google-chrome',
        '--exclude=/home/odoo/.local/share/Trash'
    ]

    # Construct the tar command with the exclude paths
    tar_command = ["tar", "-czvf", backup_path, "--ignore-failed-read"] + exclude_paths + [backup_dir]

    # Run tar command
    try:
        log_callback("Creating backup...")
        process = subprocess.Popen(tar_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Stream the output to the log_callback
        for line in process.stdout:
            log_callback(line.strip())

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, tar_command)

        log_callback(f"Backup created at {backup_path}")
    except subprocess.CalledProcessError as e:
        log_callback(f"Backup failed: {str(e)}")
        return False

    # Upload with rclone
    try:
        rclone_command = ["rclone", "copy", backup_path, f"{rclone_remote}:{gdrive_folder}/"]
        log_callback("Uploading backup to Google Drive...")
        upload_process = subprocess.Popen(rclone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Stream the rclone output to the log_callback
        for line in upload_process.stdout:
            log_callback(line.strip())

        upload_process.wait()
        if upload_process.returncode != 0:
            raise subprocess.CalledProcessError(upload_process.returncode, rclone_command)

        log_callback("Backup uploaded to Google Drive successfully.")
    except subprocess.CalledProcessError as e:
        log_callback(f"Upload failed: {str(e)}")
        return False
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            log_callback(f"Local backup file {backup_name} deleted.")

    return True



