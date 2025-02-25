import os
import sqlite3
import subprocess
import sys

# Welcome message
print("Welcome to the Home Server Setup!")
print("This script will help you configure the server and client applications.")

# Install required packages
def install_requirements():
    required_packages = [
        "tkinter",  # Built-in, no need to install
        "pyinstaller",  # For compiling to EXE
        "psutil",  # For disk usage
        "requests",  # For public IP
    ]

    print("\nInstalling required packages...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}.")

# Ask for the drive to use
def select_drive():
    drive = input("\nEnter the drive letter where you want to install the server (e.g., E:): ").strip().upper()
    if not drive.endswith(":"):
        drive += ":"
    return drive

# Create folders and database (for server)
def setup_server(drive):
    logs_folder = os.path.join(drive, "logs")
    user_folders = os.path.join(drive, "user_folders")
    database_file = os.path.join(drive, "database", "users.db")

    print("\nCreating folders...")
    try:
        os.makedirs(logs_folder, exist_ok=True)
        os.makedirs(user_folders, exist_ok=True)
        os.makedirs(os.path.dirname(database_file), exist_ok=True)
        print(f"Folders created successfully at {drive}.")
    except Exception as e:
        print(f"Error creating folders: {e}")
        exit(1)

    print("\nCreating database...")
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Database created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
        exit(1)

# Setup client (minimal setup)
def setup_client():
    print("\nClient setup complete!")
    print("You can now run `client_app.py` to connect to the server.")

# Main function
def main():
    install_requirements()

    # Ask if the machine is a server or client
    machine_type = input("\nIs this machine a server or client? (Enter 'server' or 'client'): ").strip().lower()
    if machine_type not in ["server", "client"]:
        print("Invalid input. Please enter 'server' or 'client'.")
        exit(1)

    if machine_type == "server":
        drive = select_drive()
        setup_server(drive)
        print("\nServer setup complete! Here's what you need to do next:")
        print("1. Run `server_app.py` to start the server.")
        print("2. Share the server's IP address with clients.")
    else:
        setup_client()
        print("\nClient setup complete! Here's what you need to do next:")
        print("1. Run `client_app.py` to connect to the server.")
        print("2. Enter the server's IP address when prompted.")

    print("\nThank you for using the Home Server!")

if __name__ == "__main__":
    main()