# Clinic Management System

A desktop application for managing clinic operations including departments, doctors, patients, and appointments.

## Features

- **Department Management**: Add, view, and reset departments.
- **Clinic Management**: Register clinics and associate them with departments.  
- **Doctor Management**: Register doctors with contact details and department assignments.
- **Patient Management**: Register patients with personal and contact information.
- **Appointment Scheduling**: Schedule appointments connecting patients with doctors at specific clinics.

## Technologies Used

- **Frontend**: Python with Tkinter for the GUI
- **Backend**: MySQL for database storage
- **Connection**: MySQL Connector for Python

## Requirements

- Python 3.x
- MySQL Server
- `mysql-connector-python` package

## Installation

1. Clone this repository or download the source code.
2. Install the required Python package:
   ```
   pip install mysql-connector-python
   ```
3. Configure the MySQL connection settings in `main.py`:
   ```python
   db_config = {
       'host': 'localhost',
       'user': 'root',      # Replace with your MySQL username
       'password': 'your_password',  # Replace with your MySQL password
       'database': 'clinic' # Your database name
   }
   ```

## Database Setup

When you run the application for the first time, it will:
1. Create a database named `clinic` if it doesn't exist
2. Create all necessary tables (Department, Clinic, Doctor, Patient, Appointment, Doctor_Appointment)
3. Populate the Department table with some sample data

The database schema follows this structure:
- **Department**: Stores medical departments (Cardiology, Neurology, etc.)
- **Clinic**: Physical clinic locations linked to departments
- **Doctor**: Medical staff with department assignments
- **Patient**: Patient information and demographics
- **Appointment**: Scheduled appointments with dates, times, and status
- **Doctor_Appointment**: Many-to-many relationship between doctors and appointments

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Use the tabbed interface to navigate between different sections:
   - **Departments**: Manage medical departments
   - **Clinics**: Register and view clinics
   - **Doctors**: Add and view medical staff
   - **Patients**: Register and manage patients
   - **Appointments**: Schedule and track appointments

## Screenshots

[Screenshots would be placed here]

## Contributing

Feel free to fork this repository and submit pull requests to contribute to this project.

## License

This project is open source and available under the [MIT License](LICENSE). 