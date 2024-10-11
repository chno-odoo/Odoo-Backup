# Script used to create the backup
# Written by CHNO
# Creation Date: Wed Oct  9 10:32:38 AM EDT 2024
# Last Updated: Wed Oct  9 02:20:28 PM EDT 2024
# Last Update: Added additional logging as well as disabling the run backup button while a backup is running.

import tkinter as tk
from tkinter import filedialog, messagebox
from backup import create_backup
from cron_setup import set_anacron_job

class BackupGUI:
    def __init__(self, root):
        root.title("Backup Utility")

        # GUI components for selecting backup directory, rclone config, Google Drive, and schedule.
        self.backup_dir_label = tk.Label(root, text="Backup Directory:")
        self.backup_dir_label.pack()
        self.backup_dir_entry = tk.Entry(root, width=50)
        self.backup_dir_entry.pack()
        self.backup_dir_button = tk.Button(root, text="Select Directory", command=self.select_backup_directory)
        self.backup_dir_button.pack()

        # Rclone remote config
        self.rclone_label = tk.Label(root, text="Rclone Remote Config:")
        self.rclone_label.pack()
        self.rclone_entry = tk.Entry(root, width=50)
        self.rclone_entry.pack()

        # Set default Rclone config path
        self.rclone_entry.insert(0, "gdrive:")

        # Google Drive folder name
        self.gdrive_label = tk.Label(root, text="Google Drive Folder Name:")
        self.gdrive_label.pack()
        self.gdrive_entry = tk.Entry(root, width=50)
        self.gdrive_entry.pack()

        # Backup Schedule (Daily/Weekly)
        self.schedule_label = tk.Label(root, text="Backup Schedule:")
        self.schedule_label.pack()

        self.schedule_var = tk.StringVar(value="daily")  # Default to daily
        self.daily_radio = tk.Radiobutton(root, text="Daily", variable=self.schedule_var, value="daily")
        self.weekly_radio = tk.Radiobutton(root, text="Weekly", variable=self.schedule_var, value="weekly")

        self.daily_radio.pack()
        self.weekly_radio.pack()

        # Run Backup Button
        self.submit_button = tk.Button(root, text="Run Backup", command=self.run_backup)
        self.submit_button.pack()

        # Set Anacron Job Button
        self.anacron_button = tk.Button(root, text="Set Anacron Job", command=self.set_anacron_job)
        self.anacron_button.pack()

        # Status Label
        self.status_label = tk.Label(root, text="", fg="green")
        self.status_label.pack()

        # Log output Text widget
        self.log_output = tk.Text(root, width=60, height=15)
        self.log_output.pack()

    # Function to log messages in the Text Widget.
    def log_message(self, message):
        self.log_output.insert(tk.END, f"{message}\n")
        self.log_output.see(tk.END)  # Automatically scroll to the latest message
        print(message)

    def select_backup_directory(self):
        """Function to select the backup directory."""
        dir_path = filedialog.askdirectory()
        self.backup_dir_entry.delete(0, tk.END)
        self.backup_dir_entry.insert(0, dir_path)

    def run_backup(self):
        """Function to create the backup."""
        backup_dir = self.backup_dir_entry.get()
        rclone_remote = self.rclone_entry.get()
        gdrive_folder = self.gdrive_entry.get()

        if not backup_dir or not rclone_remote or not gdrive_folder:
            self.log_message("All fields are required.")
            return

        self.log_message("Starting backup...")

        # Disable the "Run Backup" button to prevent multiple backups.
        self.submit_button.config(state=tk.DISABLED)

        # Run the backup in a new thread to avoid blocking the GUI
        import threading
        threading.Thread(target=lambda: self._run_backup_thread(backup_dir, rclone_remote, gdrive_folder)).start()

    def _run_backup_thread(self, backup_dir, rclone_remote, gdrive_folder):
        """Backup thread to avoid freezing the GUI."""

        try:
            if create_backup(backup_dir, rclone_remote, gdrive_folder, self.log_message):
                self.log_message("Backup Complete!")
            else:
                self.log_message("Backup failed. Check the logs for details.")
        except Exception as e:
            self.log_message(f"An error occurred during the backup: {str(e)}")
        finally:
            # Re-enable the "Run Backup" button after the backup completes
            self.submit_button.config(state=tk.NORMAL)


    def set_anacron_job(self):
        """Function to set the anacron job."""
        schedule = self.schedule_var.get()
        command = "python3 /home/odoo/Odoo-Backup/main.py"
        if set_anacron_job(schedule, command):
            self.log_message("Anacron Job set successfully! You may have been prompted for your password.")
        else:
            self.log_message("Failed to set Anacron Job. Check if you have root permissions.")


if __name__ == "__main__":
    root = tk.Tk()
    gui = BackupGUI(root)
    root.mainloop()
