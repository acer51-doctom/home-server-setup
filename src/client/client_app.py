import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import os
import sys
import time

# Define paths (will be updated by setup.py)
drive = "E:"  # Default, will be overridden
database_file = os.path.join(drive, "database", "users.db")

# Function to check if setup is complete
def check_setup():
    # Check if the database file exists
    if not os.path.exists(database_file):
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

# Language texts
LANGUAGES = {
    "English": {
        "title": "Client Application",
        "language_label": "Select Language:",
        "ip_label": "IP Address:",
        "username_label": "Username:",
        "password_label": "Password:",
        "login_button": "Log In",
        "login_success": "Hello {username}! Welcome to your drive.",
        "login_error": "Please fill in all fields.",
        "user_not_found": "User not found.",
        "invalid_password": "Invalid password."
    },
    "Français": {
        "title": "Application Client",
        "language_label": "Sélectionnez la langue:",
        "ip_label": "Adresse IP:",
        "username_label": "Nom d'utilisateur:",
        "password_label": "Mot de passe:",
        "login_button": "Se Connecter",
        "login_success": "Bonjour {username}! Bienvenue sur votre lecteur.",
        "login_error": "Veuillez remplir tous les champs.",
        "user_not_found": "Utilisateur non trouvé.",
        "invalid_password": "Mot de passe invalide."
    }
}

# Function to update the UI based on the selected language
def update_language():
    language = language_var.get()
    texts = LANGUAGES[language]

    root.title(texts["title"])
    language_label.config(text=texts["language_label"])
    ip_label.config(text=texts["ip_label"])
    username_label.config(text=texts["username_label"])
    password_label.config(text=texts["password_label"])
    login_button.config(text=texts["login_button"])

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    language = language_var.get()
    texts = LANGUAGES[language]

    # Validate inputs
    if not username or not password:
        messagebox.showwarning("Input Error", texts["login_error"])
        return

    # Check if user exists and password is correct
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        messagebox.showerror("Error", texts["user_not_found"])
        return
    if result[0] != password:
        messagebox.showerror("Error", texts["invalid_password"])
        return

    # Login successful
    messagebox.showinfo("Success", texts["login_success"].format(username=username))

# Main GUI
root = tk.Tk()
root.title("Client Application")

# Ask for the server's IP address on startup
server_ip = simpledialog.askstring("Server IP", "Enter the server's IP address:")
if not server_ip:
    messagebox.showerror("Error", "Server IP address is required.")
    exit()

# Make the app stretchy
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Language Selector
language_var = tk.StringVar(value="English")
language_var.trace("w", lambda *args: update_language())  # Update UI when language changes

language_label = tk.Label(root, text="Select Language:")
language_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

tk.Radiobutton(root, text="English", variable=language_var, value="English").grid(row=0, column=1, padx=10, pady=10, sticky="w")
tk.Radiobutton(root, text="Français", variable=language_var, value="Français").grid(row=0, column=2, padx=10, pady=10, sticky="w")

# Login Section
ip_label = tk.Label(root, text=f"Server IP: {server_ip}")
ip_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

username_label = tk.Label(root, text="Username:")
username_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

username_entry = tk.Entry(root)
username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

password_label = tk.Label(root, text="Password:")
password_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

password_entry = tk.Entry(root, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Buttons
login_button = tk.Button(root, text="Log In", command=login)
login_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

# Initialize language
update_language()

# Make the window resizable
root.resizable(True, True)

root.mainloop()