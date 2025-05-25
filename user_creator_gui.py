import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask
from flask_mysqldb import MySQL
from config import Config # Assuming config.py exists and defines MySQL connection details
from werkzeug.security import generate_password_hash # This import will still be present but not used for hashing
import MySQLdb.cursors
import random
import re
import time

# Setup Flask app context for DB connection
# This part is for database interaction and runs within a Flask app context.
# It's important to note that a Tkinter GUI and a Flask app are typically separate processes.
# For this example, the Flask app context is used to enable MySQLdb operations within the Tkinter app.
flask_app = Flask(__name__)
flask_app.config.from_object(Config) # Load configuration from Config class
mysql = MySQL(flask_app)

# Initialize the main Tkinter window
root = tk.Tk()
root.title("User Registration with OTP")
root.geometry("450x600") # Adjusted geometry to accommodate the new OTP display label
root.configure(bg="#e0f2f7") # Light blue background

# Styling for Tkinter widgets
style = ttk.Style()
style.theme_use("clam") # A more modern theme

# Configure styles for various widget types
style.configure("TLabel", background="#e0f2f7", font=("Segoe UI", 11))
style.configure("TEntry", font=("Segoe UI", 11), padding=5) # Added padding for entries
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10, background="#4caf50", foreground="white", relief="flat")
style.map("TButton",
    background=[("active", "#45a049")], # Darker green on hover
    foreground=[("active", "white")]
)
style.configure("TCheckbutton", background="#e0f2f7", font=("Segoe UI", 11))
style.configure("TLabelframe", background="#e0f2f7", font=("Segoe UI", 11, "bold"), borderwidth=2, relief="groove")
style.configure("TLabelframe.Label", font=("Segoe UI", 13, "bold"), foreground="#212121") # Larger and darker label for frames

# --- Combined Input Fields Section ---
# This frame will now hold all user input fields (username, password, email, OTP)
input_fields_frame = ttk.LabelFrame(root, text="User and OTP Details", padding=20)
input_fields_frame.pack(pady=(20, 10), padx=25, fill="x", expand=True)

# Username Input
ttk.Label(input_fields_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=7, padx=5)
entry_username = ttk.Entry(input_fields_frame)
entry_username.grid(row=0, column=1, sticky="ew", pady=7, padx=5)

# Password Input
ttk.Label(input_fields_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=7, padx=5)
entry_password = ttk.Entry(input_fields_frame) # Removed show="*"
entry_password.grid(row=1, column=1, sticky="ew", pady=7, padx=5)

# Confirm Password Input
ttk.Label(input_fields_frame, text="Confirm Password:").grid(row=2, column=0, sticky="w", pady=7, padx=5)
entry_confirm = ttk.Entry(input_fields_frame) # Removed show="*"
entry_confirm.grid(row=2, column=1, sticky="ew", pady=7, padx=5)

# Email Input for OTP
ttk.Label(input_fields_frame, text="Email:").grid(row=3, column=0, sticky="w", pady=7, padx=5)
entry_email_otp = ttk.Entry(input_fields_frame)
entry_email_otp.grid(row=3, column=1, sticky="ew", pady=7, padx=5)

# Label to show OTP sent status/message
otp_sent_label = ttk.Label(input_fields_frame, text="", foreground="#1976d2", font=("Segoe UI", 10, "italic"))
otp_sent_label.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

# OTP Input
ttk.Label(input_fields_frame, text="Enter OTP:").grid(row=5, column=0, sticky="w", pady=7, padx=5)
entry_otp = ttk.Entry(input_fields_frame)
entry_otp.grid(row=5, column=1, sticky="ew", pady=7, padx=5)

# Admin Checkbox
is_admin_var = tk.BooleanVar()
check_admin = ttk.Checkbutton(input_fields_frame, text="Is Admin", variable=is_admin_var)
check_admin.grid(row=6, column=0, columnspan=2, pady=10, sticky="w", padx=5)

# Configure the column to expand with the window
input_fields_frame.columnconfigure(1, weight=1)

# Global variables for OTP management
generated_otp = None
otp_expiry_time = None
otp_email_for_verification = None

# Label to display the simulated OTP directly on the GUI
# This label will be updated by simulate_send_otp function
simulated_otp_display_label = ttk.Label(input_fields_frame, text="", foreground="#d32f2f", font=("Segoe UI", 12, "bold"))
simulated_otp_display_label.grid(row=8, column=0, columnspan=2, pady=10, padx=5, sticky="ew")


# Function to validate email format using regex
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to simulate sending OTP to the entered email
def simulate_send_otp():
    global generated_otp, otp_expiry_time, otp_email_for_verification
    email = entry_email_otp.get().strip()

    if not email or not is_valid_email(email):
        messagebox.showerror("Error", "Please enter a valid email address.")
        return

    # Generate a 6-digit random OTP
    generated_otp = str(random.randint(100000, 999999))
    otp_expiry_time = time.time() + 60 # OTP valid for 60 seconds
    otp_email_for_verification = email # Store email for later verification
    otp_sent_label.config(text=f"OTP sent to {email} (Simulated)")
    
    # Display the simulated OTP directly on the GUI
    simulated_otp_display_label.config(text=f"Simulated OTP: {generated_otp} (Expires in 60s)")
    # No messagebox.showinfo here anymore

# Button to trigger OTP sending
btn_send_otp = ttk.Button(input_fields_frame, text="Send OTP", command=simulate_send_otp)
btn_send_otp.grid(row=7, column=0, columnspan=2, pady=15, padx=5) # Placed within the combined frame

# Function to handle user registration with OTP verification
def add_user_with_otp():
    global generated_otp, otp_expiry_time, otp_email_for_verification
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    confirm = entry_confirm.get().strip()
    is_admin = is_admin_var.get()
    entered_otp = entry_otp.get().strip()
    email = entry_email_otp.get().strip()

    # Validate all required fields are filled
    if not username or not password or not confirm or not email or not entered_otp:
        messagebox.showerror("Error", "All fields including email and OTP are required.")
        return

    # Check if passwords match
    if password != confirm:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    # OTP validation checks
    if generated_otp is None:
        messagebox.showerror("Error", "Please request an OTP first.")
        return

    if time.time() > otp_expiry_time:
        messagebox.showerror("Error", "OTP has expired. Please request a new one.")
        # Reset OTP variables on expiry
        generated_otp = None
        otp_expiry_time = None
        otp_email_for_verification = None
        otp_sent_label.config(text="") # Clear OTP sent message
        simulated_otp_display_label.config(text="") # Clear displayed OTP
        return

    if entered_otp != generated_otp:
        messagebox.showerror("Error", "Invalid OTP.")
        return

    if email != otp_email_for_verification:
        messagebox.showerror("Error", "The email provided does not match the email for the sent OTP.")
        return

    # Database interaction within Flask app context
    try:
        with flask_app.app_context():
            conn = mysql.connection
            cur = conn.cursor(MySQLdb.cursors.DictCursor)

            # Check if username already exists
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                messagebox.showerror("Error", "Username already exists.")
                return

            # Store the password as plain text (not hashed)
            # IMPORTANT: Storing passwords in plain text is highly insecure and not recommended for production environments.
            # This change is made only to fulfill the user's specific request.
            plain_password = password

            # Insert new user into the database
            cur.execute("""
                INSERT INTO users (username, password, is_admin)
                VALUES (%s, %s, %s)
            """, (username, plain_password, is_admin)) # Use plain_password here

            conn.commit() # Commit changes to the database
            messagebox.showinfo("Success", f"User '{username}' created successfully!")

            # Clear all input fields after successful registration
            entry_username.delete(0, tk.END)
            entry_password.delete(0, tk.END)
            entry_confirm.delete(0, tk.END)
            entry_email_otp.delete(0, tk.END)
            entry_otp.delete(0, tk.END)
            is_admin_var.set(False) # Uncheck admin checkbox
            # Reset OTP variables
            generated_otp = None
            otp_expiry_time = None
            otp_email_for_verification = None
            otp_sent_label.config(text="") # Clear OTP sent message
            simulated_otp_display_label.config(text="") # Clear displayed OTP

    except Exception as e:
        # Rollback transaction in case of error
        if conn:
            conn.rollback()
        messagebox.showerror("Database Error", str(e))

# Button to add/register the user
btn_add_user = ttk.Button(root, text="Register User", command=add_user_with_otp, style="TButton")
btn_add_user.pack(pady=20, padx=25, fill="x")

# Configure the main window's column to expand
root.columnconfigure(0, weight=1)

# Start the Tkinter event loop
root.mainloop()
