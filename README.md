# EPAPHRA Church Management System

A comprehensive church management system built with Flask, designed to help churches manage their members, cell teams, documents, marriages, and more.

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

- Financial Management
  - Track income and expenses
  - Generate financial reports
  - Budget management

- Teaching Service Management
  - Manage programs and courses
  - Track attendance
  - Resource management

- Notification System
  - Birthday and anniversary reminders
  - Event notifications
  - Real-time updates

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EPOSPEA
```

2. Create a virtual environment and activate it:
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
Open your browser and navigate to `http://localhost:3001`

## Default Login

- Username: admin
- Password: admin123

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