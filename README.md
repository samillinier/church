# EPAPHRA Church Management System

A comprehensive church management system built with Flask, designed to help churches manage their members and cell teams (Bible study groups) effectively.

## Features

- **Member Management**
  - Register new members with detailed information
  - Track member details including personal info, contact details, and church involvement
  - Search and filter member database
  
- **Cell Team Management**
  - Create and manage Bible study groups
  - Assign leaders and members to teams
  - Track meeting schedules and locations
  - Search functionality for team members

- **User Authentication**
  - Secure login system
  - Admin dashboard access
  - Protected routes

## Technology Stack

- Python 3.x
- Flask
- SQLAlchemy
- SQLite
- Bootstrap 5
- Font Awesome

## Installation

1. Clone the repository:
```bash
git clone https://github.com/samillinier/church.git
cd church
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:8080`

## Default Login

- Username: admin
- Password: admin123

*Note: Please change these credentials in a production environment*

## License

MIT License 