# EPAPHRA Church Management System

A comprehensive church management system built with Flask and SQLAlchemy.

## Features

- Member Management
  - Registration and profile management
  - Photo upload support
  - Member search and filtering
  - Member analytics

- Cell Team Management
  - Create and manage cell teams
  - Assign leaders and members
  - Track meeting schedules

- Document Management
  - Store and organize church documents
  - Document categorization
  - Search functionality

- Marriage Service Management
  - Track marriage applications
  - Manage counseling sessions
  - Document requirements tracking

- Teaching Program Management
  - Manage programs and courses
  - Track attendance
  - Resource management

- Financial Management
  - Track income and expenses
  - Generate financial reports
  - Budget management

- Role-based Access Control

- Notification System
  - Birthday and anniversary reminders
  - Event notifications
  - Real-time updates

## Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- Other dependencies in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/samillinier/church.git
cd church
```

2. Create and activate virtual environment:
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
python app.py
```

5. Access the application:
Open http://localhost:3002 in your web browser

## Default Users

The system comes with three default users:
- Admin: username: `admin`, password: `admin123`
- Finance Admin: username: `finance_admin`, password: `finance123`
- Finance Officer: username: `finance_officer`, password: `finance123`

## Directory Structure

```
EPOSPEA/
├── app.py              # Main application file
├── static/            # Static files (CSS, JS, uploads)
├── templates/         # HTML templates
├── uploads/          # User uploaded files
└── church.db         # SQLite database
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 