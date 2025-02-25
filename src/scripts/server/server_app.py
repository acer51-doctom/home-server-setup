import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sqlite3
from datetime import datetime
import psutil  # For disk usage
import socket  # For IP address
import requests  # For public IP
import sys
import time

# Define paths (will be updated by setup.py)
drive = "E:"  # Default, will be overridden
logs_folder = os.path.join(drive, "logs")
user_folders = os.path.join(drive, "user_folders")
database_file = os.path.join(drive, "database", "users.db")

# Function to check if setup is complete
def check_setup():
    # Check if required folders and files exist
    if not os.path.exists(logs_folder) or not os.path.exists(user_folders) or not os.path.exists(database_file):
        return False
    return True

# Function to display error message and exit
def show_error_and_exit():
    print("Dependencies not detected! Cannot proceed.")
    print("Please make sure to run setup.py/exe in the common folder!")
    print("Exiting app in 10 seconds...")
    time.sleep(10)
    sys.exit(1)

# Check setup before proceeding
if not check_setup():
    show_error_and_exit()

# Function to log actions
def log_action(action):
    log_file = os.path.join(logs_folder, "server_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {action}\n")

# Function to connect to the database
def connect_db():
    return sqlite3.connect(database_file)

# Function to get local IP address
def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        log_action(f"Error getting local IP: {e}")
        return "Unknown"

# Function to get public IP address
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        public_ip = response.json()["ip"]
        return public_ip
    except Exception as e:
        log_action(f"Error getting public IP: {e}")
        return "Unknown"

# Function to start the server
def start_server():
    # Get the local IP address
    local_ip = get_local_ip()
    log_action(f"Local IP: {local_ip}")

    # Get the public IP address if enabled
    if public_ip_var.get():
        public_ip = get_public_ip()
        log_action(f"Public IP: {public_ip}")
        ip_info = f"Local IP: {local_ip}\nPublic IP: {public_ip}"
    else:
        ip_info = f"Local IP: {local_ip}"

    # Log the action
    log_action("Server started.")

    # Open a new command prompt window to display server info
    subprocess.Popen(["start", "cmd", "/k", f"echo Server started. IP Info:\n{ip_info}"], shell=True)

    # Update server status
    update_server_status()

# Function to update server status
def update_server_status():
    # Get disk usage
    disk_usage = psutil.disk_usage(drive)
    disk_percent = disk_usage.percent

    # Get active users
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    active_users = len(cursor.fetchall())
    conn.close()

    # Update status label
    status_label.config(text=f"Active Users: {active_users} | Disk Usage: {disk_percent}%")

    # Schedule the next update
    root.after(5000, update_server_status)  # Update every 5 seconds

# Function to add a user
def add_user():
    def create_user():
        username = username_entry.get()
        password = password_entry.get()

        # Validate username and password
        if not username:
            messagebox.showwarning("Input Error", "Username is required.")
            return
        if not password:
            messagebox.showwarning("Input Error", "Password is required.")
            return

        # Check if user already exists
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists.")
            conn.close()
            return

        try:
            # Create user using Windows command
            subprocess.run(["net", "user", username, password, "/add"], check=True)

            # Add user to the database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

            # Create a folder for the user
            user_folder = os.path.join(user_folders, username)
            os.makedirs(user_folder, exist_ok=True)

            # Log the action
            log_action(f"User {username} created.")

            messagebox.showinfo("Success", f"User {username} created successfully!")
            add_user_window.destroy()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to create user.")
        finally:
            conn.close()

    # Create a new window for adding a user
    add_user_window = tk.Toplevel(root)
    add_user_window.title("Add User")

    tk.Label(add_user_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(add_user_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(add_user_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(add_user_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(add_user_window, text="Create", command=create_user).grid(row=2, column=0, pady=10)
    tk.Button(add_user_window, text="Cancel", command=add_user_window.destroy).grid(row=2, column=1, pady=10)

# Function to delete a user
def delete_user():
    def remove_user():
        selected_user = user_combobox.get()
        if selected_user:
            try:
                # Delete user using Windows command
                subprocess.run(["net", "user", selected_user, "/delete"], check=True)

                # Remove user from the database
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (selected_user,))
                conn.commit()

                # Delete the user's folder
                user_folder = os.path.join(user_folders, selected_user)
                if os.path.exists(user_folder):
                    os.rmdir(user_folder)

                # Log the action
                log_action(f"User {selected_user} deleted.")

                messagebox.showinfo("Success", f"User {selected_user} deleted successfully!")
                delete_user_window.destroy()
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to delete user.")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Input Error", "Please select a user.")

    # Get list of users from the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Create a new window for deleting a user
    delete_user_window = tk.Toplevel(root)
    delete_user_window.title("Delete User")

    tk.Label(delete_user_window, text="Select User:").grid(row=0, column=0, padx=10, pady=10)
    user_combobox = ttk.Combobox(delete_user_window, values=users)
    user_combobox.grid(row=0, column=1, padx=10, pady=10)

    tk.Button(delete_user_window, text="Delete", command=remove_user).grid(row=1, column=0, pady=10)
    tk.Button(delete_user_window, text="Cancel", command=delete_user_window.destroy).grid(row=1, column=1, pady=10)

# Function to end the session and save logs
def end_session():
    log_file = os.path.join(logs_folder, "server_log.txt")
    with open(log_file, "r") as f:
        logs = f.read()
    messagebox.showinfo("Session Logs", logs)
    log_action("Session ended.")
    root.destroy()  # Close the server application

# Main GUI
root = tk.Tk()
root.title("Server Manager")

# Public IP Switch
public_ip_var = tk.BooleanVar(value=False)
public_ip_switch = tk.Checkbutton(root, text="Use Public IP", variable=public_ip_var)
public_ip_switch.pack(pady=10)

# Buttons
tk.Button(root, text="Start Server", command=start_server).pack(pady=10)
tk.Button(root, text="Add User", command=add_user).pack(pady=10)
tk.Button(root, text="Delete User", command=delete_user).pack(pady=10)
tk.Button(root, text="End Session", command=end_session).pack(pady=10)

# Status Label
status_label = tk.Label(root, text="Server Status: Not Running")
status_label.pack(pady=10)

root.mainloop()