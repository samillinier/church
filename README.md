# EPAPHRA Church Management System

A comprehensive church management system built with Flask.

## Features

- Member Management
- Cell Team Management
- Document Management
- Marriage Service Management
- Teaching Program Management
- Financial Management
- User Authentication and Authorization
- Notifications System

## Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url  # Optional, will use SQLite by default
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set up environment variables in Vercel:
- Go to your project settings in Vercel dashboard
- Add the following environment variables:
  - `DATABASE_URL`: Your PostgreSQL database URL
  - `SECRET_KEY`: Your secret key
  - `FLASK_ENV`: production

5. Deploy to production:
```bash
vercel --prod
```

## Default Users

After initialization, the following users are created:

1. Admin User
- Username: admin
- Password: admin123

2. Finance Admin
- Username: finance_admin
- Password: finance123

3. Finance Officer
- Username: finance_officer
- Password: officer123

## Database Configuration

The application supports both SQLite (development) and PostgreSQL (production) databases:
- Local development uses SQLite by default
- Production deployment uses PostgreSQL (requires `DATABASE_URL` environment variable)

## File Structure

```
├── app.py              # Main application file
├── vercel_app.py       # Vercel entry point
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel configuration
├── static/            # Static files
└── templates/         # HTML templates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 