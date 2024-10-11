# This script will be used to create the functions needed for the cron job setup.
# Written by Chno
# Creation Date: Wed Oct  9 08:19:11 AM EDT 2024
# Last Updated: Wed Oct  9 02:57:03 PM EDT 2024
# Last Update: Added pkexec for GUI Authentication.

import subprocess
import os
import logging

def set_anacron_job(schedule, command, job_name="backup job", delay=5):
    """
    Set up an anacron job for the specified schedule.

    :param schedule: The schedule for the anacron job ('daily' or 'weekly').
    :param command: The command to be executed by the anacron job.
    :param job_name: The job identifier in anacron (default is 'backup-job').
    :param delay: The delay in minutes before running the job after boot (default is 5 minutes).
    :return: True if successful, False otherwise.
    """

    # Define the period for the anacron job based on the schedule
    if schedule == "daily":
        period = 1
    elif schedule == "weekly":
        period = 7
    else:
        logging.error(f"Unsupported schedule: {schedule}")
        return False

    # Define the anacron entry line
    anacron_entry = f"{period} {delay} {job_name} {command}\n"

    try:
        # Read the current /etc/anacrontab content using pkexec
        read_command = ["pkexec", "cat", "/etc/anacrontab"]
        current_content = subprocess.run(read_command, check=True, text=True, capture_output=True).stdout

        # Check if the job already exists to avoid duplication
        if anacron_entry.strip() in current_content:
            logging.info(f"The anacron job '{job_name}' is already set.")
            return True

        # Append the new job to /etc/anacrontab using pkexec
        append_command = f"echo '{anacron_entry.strip()}' | pkexec tee -a /etc/anacrontab > /dev/null"
        subprocess.run(append_command, shell=True, check=True)
        logging.info(f"Anacron job set successfully: {anacron_entry.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to set up anacron job: {e}")
        return False
