import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime

# MySQL Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',      # Replace with your MySQL username
    'password': 'Hazem@2003',      # Replace with your MySQL password
    'database': 'clinic', # Your database name
    'autocommit': False,  # Required for transaction management
    'pool_name': 'clinic_pool',
    'pool_size': 5
}

# Try to connect to MySQL, create database if it doesn't exist
try:
    # First connect without specifying a database
    temp_conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    temp_cursor = temp_conn.cursor()
    
    # Create the database if it doesn't exist
    temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    temp_conn.commit()
    temp_conn.close()
    
    # Now connect with the pool to the created database
    conn_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name=db_config['pool_name'],
        pool_size=db_config['pool_size'],
        **{k: v for k, v in db_config.items() if k not in ['pool_name', 'pool_size']}
    )
    
    # Get a connection from the pool
    conn = conn_pool.get_connection()
    cursor = conn.cursor()
    
    print(f"Connected to MySQL, using database: {db_config['database']}")
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Failed to connect to MySQL: {err}")
    exit(1)

# Drop all tables first to ensure clean schema (for testing)
try:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DROP TABLE IF EXISTS Doctor_Appointment")
    cursor.execute("DROP TABLE IF EXISTS Appointment")
    cursor.execute("DROP TABLE IF EXISTS Doctor")
    cursor.execute("DROP TABLE IF EXISTS Clinic")
    cursor.execute("DROP TABLE IF EXISTS Patient")
    cursor.execute("DROP TABLE IF EXISTS Department")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("Dropped all existing tables")
except mysql.connector.Error as err:
    print(f"Error dropping tables: {err}")
    conn.rollback()

# Ensure tables exist (run once)
cursor.execute('''CREATE TABLE IF NOT EXISTS Department (
    D_ID INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (D_ID)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Clinic (
    C_ID INT AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL, 
    address VARCHAR(255), 
    FK_D_ID INT,
    PRIMARY KEY (C_ID),
    FOREIGN KEY (FK_D_ID) REFERENCES Department(D_ID)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Doctor (
    Do_ID INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, 
    phone_number VARCHAR(20),
    address VARCHAR(255), 
    FK_D_ID INT,
    PRIMARY KEY (Do_ID),
    FOREIGN KEY (FK_D_ID) REFERENCES Department(D_ID)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Patient (
    P_ID INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, 
    Job VARCHAR(100),
    birth_date DATE, 
    phone_number VARCHAR(20), 
    address VARCHAR(255),
    PRIMARY KEY (P_ID)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Appointment (
    A_ID INT AUTO_INCREMENT,
    Date DATE, 
    start_time TIME,
    End_time TIME, 
    status VARCHAR(50), 
    cost DECIMAL(10,2),
    FK_P_ID INT,
    FK_C_ID INT,
    PRIMARY KEY (A_ID),
    FOREIGN KEY (FK_P_ID) REFERENCES Patient(P_ID),
    FOREIGN KEY (FK_C_ID) REFERENCES Clinic(C_ID)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Doctor_Appointment (
    FK_Do_ID INT,
    FK_A_ID INT,
    PRIMARY KEY (FK_Do_ID, FK_A_ID),
    FOREIGN KEY (FK_Do_ID) REFERENCES Doctor(Do_ID),
    FOREIGN KEY (FK_A_ID) REFERENCES Appointment(A_ID)
)''')

conn.commit()
print("Created all tables")

# Check if there are any departments, if not, add sample departments
cursor.execute("SELECT COUNT(*) FROM Department")
dept_count = cursor.fetchone()[0]
if dept_count == 0:
    # Add sample departments
    sample_departments = [
        ('Cardiology',),
        ('Neurology',),
        ('Skeletal',),
        ('Molecular',),
        ('Digestive',)
    ]
    cursor.executemany("INSERT INTO Department (name) VALUES (%s)", sample_departments)
    conn.commit()
    print("Added sample departments")

conn.commit()

# GUI
root = tk.Tk()
root.title("Clinic Management System")
root.geometry("800x600")

# Create notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create tabs
tab_department = ttk.Frame(notebook)
tab_clinic = ttk.Frame(notebook)
tab_doctor = ttk.Frame(notebook)
tab_patient = ttk.Frame(notebook)
tab_appointment = ttk.Frame(notebook)

notebook.add(tab_department, text="Departments")
notebook.add(tab_clinic, text="Clinics")
notebook.add(tab_doctor, text="Doctors")
notebook.add(tab_patient, text="Patients")
notebook.add(tab_appointment, text="Appointments")

# ========================= DEPARTMENTS TAB =========================
# Add Department Frame
frame_add_dept = ttk.LabelFrame(tab_department, text="Add Department")
frame_add_dept.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_dept, text="Department Name:").grid(row=0, column=0, padx=5, pady=5)
dept_name_var = tk.StringVar()
tk.Entry(frame_add_dept, textvariable=dept_name_var).grid(row=0, column=1, padx=5, pady=5)

def add_dept():
    name = dept_name_var.get()
    if not name:
        messagebox.showerror("Error", "Please enter department name")
        return
    
    try:
        cursor.execute("INSERT INTO Department (name) VALUES (%s)", (name,))
        conn.commit()
        
        # Debug: Confirm the department was added
        cursor.execute("SELECT D_ID, name FROM Department WHERE name=%s", (name,))
        new_dept = cursor.fetchone()
        print(f"Added new department: {new_dept}")
        
        dept_name_var.set("")
        refresh_departments()
        refresh_department_view()
        
        # Show confirmation message
        messagebox.showinfo("Success", f"Department '{name}' added successfully!")
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add department: {err}")
        print(f"Error adding department: {err}")

def reset_departments():
    if messagebox.askyesno("Reset Departments", "This will delete all departments and add sample ones. Continue?"):
        try:
            # Drop and recreate the department table
            cursor.execute("DELETE FROM Department")
            print("Deleted all departments")
            
            # Add sample departments
            sample_departments = [
                ('Cardiology',),
                ('Neurology',),
                ('Skeletal',),
                ('Molecular',),
                ('Digestive',)
            ]
            cursor.executemany("INSERT INTO Department (name) VALUES (%s)", sample_departments)
            conn.commit()
            print("Added sample departments to database")
            
            # Verify departments were added
            cursor.execute("SELECT D_ID, name FROM Department")
            depts = cursor.fetchall()
            print(f"Current departments in database: {depts}")
            
            refresh_departments()
            refresh_department_view()
            messagebox.showinfo("Success", "Departments reset successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset departments: {str(e)}")

# Layout the buttons
button_frame = ttk.Frame(frame_add_dept)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

tk.Button(button_frame, text="Add Department", command=add_dept).pack(side="left", padx=5)
tk.Button(button_frame, text="Reset to Samples", command=reset_departments).pack(side="left", padx=5)

# View Departments Frame
frame_view_dept = ttk.LabelFrame(tab_department, text="All Departments")
frame_view_dept.pack(fill="both", expand=True, padx=10, pady=5)

dept_columns = ("D_ID", "Name")
dept_tree = ttk.Treeview(frame_view_dept, columns=dept_columns, show="headings")
for col in dept_columns:
    dept_tree.heading(col, text=col)
    dept_tree.column(col, width=100)
dept_tree.pack(fill="both", expand=True)

def refresh_department_view():
    for row in dept_tree.get_children():
        dept_tree.delete(row)
    cursor.execute("SELECT D_ID, name FROM Department")
    for row in cursor.fetchall():
        dept_tree.insert("", "end", values=row)

refresh_department_view()

# ========================= CLINICS TAB =========================
# Add Clinic Frame
frame_add_clinic = ttk.LabelFrame(tab_clinic, text="Add Clinic")
frame_add_clinic.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_clinic, text="Clinic Name:").grid(row=0, column=0, padx=5, pady=5)
clinic_name_var = tk.StringVar()
tk.Entry(frame_add_clinic, textvariable=clinic_name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_add_clinic, text="Address:").grid(row=1, column=0, padx=5, pady=5)
clinic_address_var = tk.StringVar()
tk.Entry(frame_add_clinic, textvariable=clinic_address_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_add_clinic, text="Department:").grid(row=2, column=0, padx=5, pady=5)
dept_var = tk.StringVar()
dept_combo = ttk.Combobox(frame_add_clinic, textvariable=dept_var, state="readonly")
dept_combo.grid(row=2, column=1, padx=5, pady=5)

def refresh_departments():
    cursor.execute("SELECT D_ID, name FROM Department")
    depts = cursor.fetchall()
    
    # Clear existing values
    dept_combo['values'] = []
    if 'doctor_dept_combo' in globals() and doctor_dept_combo.winfo_exists():
        doctor_dept_combo['values'] = []
    
    # Update with fresh values
    dept_values = [f"{d[0]} - {d[1]}" for d in depts]
    dept_combo['values'] = dept_values
    
    if 'doctor_dept_combo' in globals() and doctor_dept_combo.winfo_exists():
        doctor_dept_combo['values'] = dept_values
    
    # Select first value if available
    if dept_values:
        dept_combo.current(0)
        if 'doctor_dept_combo' in globals() and doctor_dept_combo.winfo_exists():
            doctor_dept_combo.current(0)

    print(f"Refreshed departments: {dept_values}")

def add_clinic():
    name = clinic_name_var.get()
    address = clinic_address_var.get()
    dept = dept_var.get()
    if not name or not dept:
        messagebox.showerror("Error", "Please enter all fields.")
        return
    
    try:
        dept_id = int(dept.split(" - ")[0])
        cursor.execute("INSERT INTO Clinic (Name, address, FK_D_ID) VALUES (%s, %s, %s)", (name, address, dept_id))
        conn.commit()
        messagebox.showinfo("Success", "Clinic added!")
        clinic_name_var.set("")
        clinic_address_var.set("")
        refresh_clinics()
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add clinic: {err}")
        print(f"Error adding clinic: {err}")

tk.Button(frame_add_clinic, text="Add Clinic", command=add_clinic).grid(row=3, column=0, columnspan=2, pady=10)

# View Clinics Frame
frame_view_clinic = ttk.LabelFrame(tab_clinic, text="All Clinics")
frame_view_clinic.pack(fill="both", expand=True, padx=10, pady=5)

clinic_columns = ("C_ID", "Name", "Address", "Department")
clinic_tree = ttk.Treeview(frame_view_clinic, columns=clinic_columns, show="headings")
for col in clinic_columns:
    clinic_tree.heading(col, text=col)
    clinic_tree.column(col, width=100)
clinic_tree.pack(fill="both", expand=True)

def refresh_clinics():
    for row in clinic_tree.get_children():
        clinic_tree.delete(row)
    cursor.execute('''SELECT Clinic.C_ID, Clinic.Name, Clinic.address, Department.name
                      FROM Clinic LEFT JOIN Department ON Clinic.FK_D_ID = Department.D_ID''')
    for row in cursor.fetchall():
        clinic_tree.insert("", "end", values=row)

refresh_clinics()

# ========================= DOCTORS TAB =========================
# Add Doctor Frame
frame_add_doctor = ttk.LabelFrame(tab_doctor, text="Add Doctor")
frame_add_doctor.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_doctor, text="Doctor Name:").grid(row=0, column=0, padx=5, pady=5)
doctor_name_var = tk.StringVar()
tk.Entry(frame_add_doctor, textvariable=doctor_name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_add_doctor, text="Phone Number:").grid(row=1, column=0, padx=5, pady=5)
doctor_phone_var = tk.StringVar()
tk.Entry(frame_add_doctor, textvariable=doctor_phone_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_add_doctor, text="Address:").grid(row=2, column=0, padx=5, pady=5)
doctor_address_var = tk.StringVar()
tk.Entry(frame_add_doctor, textvariable=doctor_address_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_add_doctor, text="Department:").grid(row=3, column=0, padx=5, pady=5)
doctor_dept_var = tk.StringVar()
doctor_dept_combo = ttk.Combobox(frame_add_doctor, textvariable=doctor_dept_var, state="readonly")
doctor_dept_combo.grid(row=3, column=1, padx=5, pady=5)

def add_doctor():
    name = doctor_name_var.get()
    phone = doctor_phone_var.get()
    address = doctor_address_var.get()
    dept = doctor_dept_var.get()
    
    if not name or not dept:
        messagebox.showerror("Error", "Please enter all required fields.")
        return
    
    try:
        dept_id = int(dept.split(" - ")[0])
        cursor.execute("INSERT INTO Doctor (name, phone_number, address, FK_D_ID) VALUES (%s, %s, %s, %s)", 
                      (name, phone, address, dept_id))
        conn.commit()
        messagebox.showinfo("Success", "Doctor added!")
        doctor_name_var.set("")
        doctor_phone_var.set("")
        doctor_address_var.set("")
        refresh_doctors()
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add doctor: {err}")
        print(f"Error adding doctor: {err}")

tk.Button(frame_add_doctor, text="Add Doctor", command=add_doctor).grid(row=4, column=0, columnspan=2, pady=10)

# View Doctors Frame
frame_view_doctor = ttk.LabelFrame(tab_doctor, text="All Doctors")
frame_view_doctor.pack(fill="both", expand=True, padx=10, pady=5)

doctor_columns = ("Do_ID", "Name", "Phone", "Address", "Department")
doctor_tree = ttk.Treeview(frame_view_doctor, columns=doctor_columns, show="headings")
for col in doctor_columns:
    doctor_tree.heading(col, text=col)
    doctor_tree.column(col, width=100)
doctor_tree.pack(fill="both", expand=True)

def refresh_doctors():
    for row in doctor_tree.get_children():
        doctor_tree.delete(row)
    cursor.execute('''SELECT Doctor.Do_ID, Doctor.name, Doctor.phone_number, Doctor.address, Department.name
                      FROM Doctor LEFT JOIN Department ON Doctor.FK_D_ID = Department.D_ID''')
    for row in cursor.fetchall():
        doctor_tree.insert("", "end", values=row)

refresh_doctors()

# ========================= PATIENTS TAB =========================
# Add Patient Frame
frame_add_patient = ttk.LabelFrame(tab_patient, text="Add Patient")
frame_add_patient.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add_patient, text="Patient Name:").grid(row=0, column=0, padx=5, pady=5)
patient_name_var = tk.StringVar()
tk.Entry(frame_add_patient, textvariable=patient_name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_add_patient, text="Job:").grid(row=1, column=0, padx=5, pady=5)
patient_job_var = tk.StringVar()
tk.Entry(frame_add_patient, textvariable=patient_job_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_add_patient, text="Birth Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
patient_birth_var = tk.StringVar()
tk.Entry(frame_add_patient, textvariable=patient_birth_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_add_patient, text="Phone Number:").grid(row=3, column=0, padx=5, pady=5)
patient_phone_var = tk.StringVar()
tk.Entry(frame_add_patient, textvariable=patient_phone_var).grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_add_patient, text="Address:").grid(row=4, column=0, padx=5, pady=5)
patient_address_var = tk.StringVar()
tk.Entry(frame_add_patient, textvariable=patient_address_var).grid(row=4, column=1, padx=5, pady=5)

def add_patient():
    name = patient_name_var.get()
    job = patient_job_var.get()
    birth_date = patient_birth_var.get()
    phone = patient_phone_var.get()
    address = patient_address_var.get()
    
    if not name:
        messagebox.showerror("Error", "Please enter patient name.")
        return
    
    try:
        cursor.execute("INSERT INTO Patient (name, Job, birth_date, phone_number, address) VALUES (%s, %s, %s, %s, %s)", 
                      (name, job, birth_date, phone, address))
        conn.commit()
        messagebox.showinfo("Success", "Patient added!")
        patient_name_var.set("")
        patient_job_var.set("")
        patient_birth_var.set("")
        patient_phone_var.set("")
        patient_address_var.set("")
        refresh_patients()
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add patient: {err}")
        print(f"Error adding patient: {err}")

tk.Button(frame_add_patient, text="Add Patient", command=add_patient).grid(row=5, column=0, columnspan=2, pady=10)

# View Patients Frame
frame_view_patient = ttk.LabelFrame(tab_patient, text="All Patients")
frame_view_patient.pack(fill="both", expand=True, padx=10, pady=5)

patient_columns = ("P_ID", "Name", "Job", "Birth Date", "Phone", "Address")
patient_tree = ttk.Treeview(frame_view_patient, columns=patient_columns, show="headings")
for col in patient_columns:
    patient_tree.heading(col, text=col)
    patient_tree.column(col, width=100)
patient_tree.pack(fill="both", expand=True)

def refresh_patients():
    for row in patient_tree.get_children():
        patient_tree.delete(row)
    cursor.execute("SELECT P_ID, name, Job, birth_date, phone_number, address FROM Patient")
    for row in cursor.fetchall():
        patient_tree.insert("", "end", values=row)

refresh_patients()

# ========================= APPOINTMENTS TAB =========================
# Add Appointment Frame
frame_add_appointment = ttk.LabelFrame(tab_appointment, text="Add Appointment")
frame_add_appointment.pack(fill="x", padx=10, pady=5)

# First row - Patient and Clinic
frame_app_row1 = ttk.Frame(frame_add_appointment)
frame_app_row1.pack(fill="x", padx=5, pady=5)

tk.Label(frame_app_row1, text="Patient:").pack(side="left", padx=5)
patient_var = tk.StringVar()
patient_combo = ttk.Combobox(frame_app_row1, textvariable=patient_var, state="readonly", width=20)
patient_combo.pack(side="left", padx=5)

tk.Label(frame_app_row1, text="Clinic:").pack(side="left", padx=5)
clinic_var = tk.StringVar()
clinic_combo = ttk.Combobox(frame_app_row1, textvariable=clinic_var, state="readonly", width=20)
clinic_combo.pack(side="left", padx=5)

# Second row - Date and Times
frame_app_row2 = ttk.Frame(frame_add_appointment)
frame_app_row2.pack(fill="x", padx=5, pady=5)

tk.Label(frame_app_row2, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
date_var = tk.StringVar()
tk.Entry(frame_app_row2, textvariable=date_var, width=12).pack(side="left", padx=5)

tk.Label(frame_app_row2, text="Start Time (HH:MM):").pack(side="left", padx=5)
start_time_var = tk.StringVar()
tk.Entry(frame_app_row2, textvariable=start_time_var, width=8).pack(side="left", padx=5)

tk.Label(frame_app_row2, text="End Time (HH:MM):").pack(side="left", padx=5)
end_time_var = tk.StringVar()
tk.Entry(frame_app_row2, textvariable=end_time_var, width=8).pack(side="left", padx=5)

# Third row - Status, Cost and Doctor
frame_app_row3 = ttk.Frame(frame_add_appointment)
frame_app_row3.pack(fill="x", padx=5, pady=5)

tk.Label(frame_app_row3, text="Status:").pack(side="left", padx=5)
status_var = tk.StringVar()
status_combo = ttk.Combobox(frame_app_row3, textvariable=status_var, width=15)
status_combo['values'] = ("Scheduled", "Completed", "Canceled")
status_combo.current(0)
status_combo.pack(side="left", padx=5)

tk.Label(frame_app_row3, text="Cost:").pack(side="left", padx=5)
cost_var = tk.StringVar()
tk.Entry(frame_app_row3, textvariable=cost_var, width=10).pack(side="left", padx=5)

tk.Label(frame_app_row3, text="Doctor:").pack(side="left", padx=5)
doctor_var = tk.StringVar()
doctor_combo = ttk.Combobox(frame_app_row3, textvariable=doctor_var, state="readonly", width=20)
doctor_combo.pack(side="left", padx=5)

def refresh_combos():
    # Refresh patients
    cursor.execute("SELECT P_ID, name FROM Patient")
    patients = cursor.fetchall()
    patient_combo['values'] = [f"{p[0]} - {p[1]}" for p in patients]
    
    # Refresh clinics
    cursor.execute("SELECT C_ID, Name FROM Clinic")
    clinics = cursor.fetchall()
    clinic_combo['values'] = [f"{c[0]} - {c[1]}" for c in clinics]
    
    # Refresh doctors
    cursor.execute("SELECT Do_ID, name FROM Doctor")
    doctors = cursor.fetchall()
    doctor_combo['values'] = [f"{d[0]} - {d[1]}" for d in doctors]

def add_appointment():
    if not patient_var.get() or not clinic_var.get() or not date_var.get() or not doctor_var.get():
        messagebox.showerror("Error", "Please fill out all required fields")
        return
    
    try:
        patient_id = int(patient_var.get().split(" - ")[0])
        clinic_id = int(clinic_var.get().split(" - ")[0])
        doctor_id = int(doctor_var.get().split(" - ")[0])
        
        # Insert appointment
        cursor.execute("""
            INSERT INTO Appointment (Date, start_time, End_time, status, cost, FK_P_ID, FK_C_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (date_var.get(), start_time_var.get(), end_time_var.get(), 
             status_var.get(), cost_var.get(), patient_id, clinic_id))
        
        # Get the last inserted appointment ID
        appointment_id = cursor.lastrowid
        
        # Link doctor to appointment
        cursor.execute("""
            INSERT INTO Doctor_Appointment (FK_Do_ID, FK_A_ID)
            VALUES (%s, %s)
        """, (doctor_id, appointment_id))
        
        # Commit the transaction
        conn.commit()
        messagebox.showinfo("Success", "Appointment added successfully!")
        
        # Clear fields
        date_var.set("")
        start_time_var.set("")
        end_time_var.set("")
        cost_var.set("")
        status_var.set("Scheduled")
        
        refresh_appointments()
        
    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
    except mysql.connector.Error as err:
        # Rollback the transaction on error
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add appointment: {err}")
        print(f"Error adding appointment: {err}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        print(f"Unexpected error: {str(e)}")

tk.Button(frame_add_appointment, text="Add Appointment", command=add_appointment).pack(pady=10)

# View Appointments Frame
frame_view_appointment = ttk.LabelFrame(tab_appointment, text="All Appointments")
frame_view_appointment.pack(fill="both", expand=True, padx=10, pady=5)

appointment_columns = ("A_ID", "Patient", "Date", "Time", "Status", "Cost", "Clinic", "Doctor")
appointment_tree = ttk.Treeview(frame_view_appointment, columns=appointment_columns, show="headings")
for col in appointment_columns:
    appointment_tree.heading(col, text=col)
    appointment_tree.column(col, width=80)
appointment_tree.pack(fill="both", expand=True)

def refresh_appointments():
    for row in appointment_tree.get_children():
        appointment_tree.delete(row)
    
    try:
        cursor.execute("""
            SELECT a.A_ID, p.name, a.Date, CONCAT(a.start_time, ' - ', a.End_time), 
                a.status, a.cost, c.Name, d.name
            FROM Appointment a
            JOIN Patient p ON a.FK_P_ID = p.P_ID
            JOIN Clinic c ON a.FK_C_ID = c.C_ID
            LEFT JOIN Doctor_Appointment da ON a.A_ID = da.FK_A_ID
            LEFT JOIN Doctor d ON da.FK_Do_ID = d.Do_ID
        """)
        
        for row in cursor.fetchall():
            appointment_tree.insert("", "end", values=row)
    except mysql.connector.Error as err:
        print(f"Error refreshing appointments: {err}")
        # If no appointments exist yet, this is fine
        pass

# Initialize all data
refresh_department_view()  # Make sure to refresh departments view first
refresh_departments()      # Then refresh department dropdowns
refresh_clinics()
refresh_doctors()
refresh_patients()
refresh_combos()
refresh_appointments()

# Close connection when application exits
def on_closing():
    if conn:
        conn.close()
        print("Database connection closed")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()