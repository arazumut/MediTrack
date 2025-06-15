# MediTrack - Clinical Patient Tracking and Appointment System

MediTrack is a comprehensive patient tracking and appointment management system designed for healthcare centers. This system includes essential clinical functions such as patient records, appointment scheduling, treatment history, and prescription management.

## Features

- **User and Role Management**: Patient, doctor, receptionist, and admin roles
- **Patient Management**: Patient registration, profile editing, treatment history viewing
- **Appointment System**: Creating, updating, canceling, and viewing appointments
- **Treatment and Prescription Management**: Adding treatment notes, diagnoses, and prescription recommendations
- **Notification System**: Appointment reminders (via email)
- **Comprehensive Authorization**: Special permissions and limitations for each user role

## Installation

1. Make sure Python 3.8+ is installed
2. Clone this project
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Perform database migrations:
   ```
   python manage.py migrate
   ```
7. Load sample data and admin user:
   ```
   python manage.py loaddata initial_data
   ```
8. Start the server:
   ```
   python manage.py runserver
   ```

## Sample Users

The following sample users can be used to test the system:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| doctor1 | doctor123 | Doctor |
| doctor2 | doctor123 | Doctor |
| reception1 | reception123 | Receptionist |
| patient1 | patient123 | Patient |
| patient2 | patient123 | Patient |

## User Roles and Permissions

| Role | Permissions |
|------|-------------|
| Patient | - Can view their own appointments<br>- Can view their own treatment history<br>- Can update their own profile |
| Doctor | - Can view their own appointments<br>- Can add treatments and prescriptions to their patients<br>- Can view information about their patients |
| Receptionist | - Can create patient records<br>- Can create and update appointments<br>- Can view all patients and appointments |
| Admin | - Full system access<br>- Can manage all users<br>- Can view and edit all data |

## Technologies

- Django 5.2
- SQLite (for development)
- Bootstrap 5
- JavaScript

## Screenshots

<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 38" src="https://github.com/user-attachments/assets/08e809ee-f8b1-497e-aed0-649e98d03ad7" />

<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 42" src="https://github.com/user-attachments/assets/9de98ddc-d74d-40ca-a96b-0f71fe205b2d" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 11 03" src="https://github.com/user-attachments/assets/01ccd4f5-3e33-460b-b64f-1323187f34a1" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 50" src="https://github.com/user-attachments/assets/bb5cbe50-643c-4fa3-8f4b-efbe1a9150ea" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 46" src="https://github.com/user-attachments/assets/e5073729-d999-4352-9b0f-2e6f07988d10" />


## License

This project is licensed under the Apache 2.0 License.

## Contact

Please get in touch with any questions or feedback.

---

Developer: K. Umut Araz 
