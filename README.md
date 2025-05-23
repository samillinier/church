# EPAPHRA Church Management System

A comprehensive church management system built with Flask, designed to help churches efficiently manage their members, cell teams, teaching programs, finances, and more.

## Features

- **Member Management**
  - Member registration and profiles
  - Member analytics and reporting
  - Contact information and emergency contacts
  - Baptism and membership status tracking

- **Cell Team Management**
  - Create and manage cell teams
  - Assign leaders and members
  - Track meeting schedules and locations
  - Monitor team activities

- **Teaching Service**
  - Program management
  - Teacher assignments
  - Student enrollment
  - Teaching materials and resources
  - Event planning and tracking

- **Finance Management**
  - Income and expense tracking
  - Budget management
  - Financial reporting
  - Category-based organization
  - Transaction history

- **Document Management**
  - Create and store church documents
  - Document categorization
  - File attachments
  - Access control

- **Marriage Service**
  - Marriage application processing
  - Counseling session tracking
  - Document requirements
  - Wedding event planning

- **Appointment System**
  - Schedule appointments
  - Counseling session management
  - Availability tracking
  - Notification system

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd EPOSPEA
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:3000`

## Default Admin Account
- Username: admin
- Password: admin123

## Technology Stack

- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy ORM
- Frontend: Bootstrap 5, Chart.js
- Icons: Font Awesome
- Authentication: Flask-Login

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 