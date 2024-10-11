# Script used to handle the entering of the password for sudo purposes.
# Written by CHNO
# Creation Date: Wed Oct  9 02:22:41 PM EDT 2024
# Last Updated: N/A
# Last Update: Initial code commit

import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw() #  Hide the root window

# Display the password prompt
password = simpledialog.askstring("Password", "Enter your sudo password: ", show='*')

# Print the password to stdout which sudo will read.
if password:
    print(password)

