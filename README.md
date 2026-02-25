# HR Nexus - Attendance & Payroll System

A comprehensive HR management system built with Django REST Framework and vanilla JavaScript. Features role-based access control, employee management, attendance tracking, leave management, and payroll processing.

## Features

### Admin Dashboard
- **Employee Management**: View, edit, and activate employee profiles
- **Pending Employees Notification**: Visual notification system for new employee signups
- **Attendance Tracking**: Monitor daily attendance, clock in/out times
- **Leave Management**: Approve or reject leave requests
- **Payroll Processing**: Generate and manage employee payslips
- **Dashboard Analytics**: Real-time statistics and insights

### Employee Dashboard
- **Personal Profile**: View and manage personal information
- **My Attendance**: Track personal attendance history
- **Leave Requests**: Submit and track leave applications
- **Payslips**: View and download salary statements
- **Restricted Access**: Employees can only view their own data

### Authentication System
- **Token-Based Authentication**: Secure REST API access
- **Role-Based Access Control**: Admin and Employee roles
- **Self-Registration**: Employees can sign up (pending admin approval)
- **Secure Login/Logout**: Protected endpoints with token management

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: SQLite (db_auth.sqlite3)
- **Frontend**: Vanilla JavaScript, Tailwind CSS
- **Authentication**: Token Authentication
- **Icons**: Lucide Icons

## Project Structure

```
ALP/
├── employees/              # Main Django app
│   ├── models.py          # User, Employee, Attendance, Leave, Payroll models
│   ├── serializers.py     # DRF serializers for API
│   ├── views.py           # API viewsets
│   ├── views_auth.py      # Authentication endpoints
│   └── urls.py            # API routes
├── frontend/
│   └── static/
│       ├── api.js                    # API helper functions
│       ├── admin_extensions.js       # Admin-specific features
│       └── employee_dashboard.js     # Employee dashboard logic
├── hr_nexus/              # Django project settings
│   ├── settings.py        # Project configuration
│   └── urls.py            # Main URL routing
├── templates/             # HTML templates
│   ├── index.html                # Admin dashboard
│   ├── employee_dashboard.html   # Employee dashboard
│   ├── login.html                # Login page
│   └── signup.html               # Registration page
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── setup.bat             # Setup script (creates venv, installs deps)
└── runserver.bat         # Start development server
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd ALP
   ```

2. **Run setup script** (creates virtual environment and installs dependencies)
   ```bash
   setup.bat
   ```

   Or manually:
   ```bash
   # Create virtual environment
   python -m venv alp

   # Activate virtual environment
   alp\Scripts\activate.bat

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations
   python manage.py migrate
   ```

3. **Create admin user** (optional, if not exists)
   ```bash
   python manage.py createsuperuser
   ```

4. **Start the server**
   ```bash
   runserver.bat
   ```
   Or: `python manage.py runserver`

5. **Access the application**
   - Admin Dashboard: http://127.0.0.1:8000/
   - Employee Dashboard: http://127.0.0.1:8000/employee/
   - Login: http://127.0.0.1:8000/login
   - Signup: http://127.0.0.1:8000/signup

## Default Credentials

- **Admin**: `admin` / `admin123`
- **Employee**: `kevs` / `kevin123`

## Usage Guide

### For Administrators

1. **Login** at http://127.0.0.1:8000/login with admin credentials
2. **Dashboard**: View system statistics and recent activity
3. **Pending Employees**: 
   - Click the yellow "Pending Employees" button (shows notification badge)
   - Review new employee signups
   - Click "Setup Profile" for each employee
   - Configure department, position, salary
   - Change status to "Active" to deploy
4. **Manage Employees**: View, edit, or delete employee records
5. **Attendance**: Track and manage employee attendance
6. **Leave Management**: Approve or reject leave requests
7. **Payroll**: Process and manage employee payroll

### For Employees

1. **Sign Up** at http://127.0.0.1:8000/signup
   - Fill in personal details
   - Account created with "Pending" status
   - Wait for admin to activate account
2. **Login** after activation at http://127.0.0.1:8000/login
3. **Dashboard**: View personal statistics
4. **My Attendance**: Check attendance history
5. **My Leaves**: Submit and track leave requests
6. **My Payslips**: View salary statements
7. **My Profile**: Update personal information

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user

### Employees
- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create employee
- `GET /api/employees/{id}/` - Get employee details
- `PUT /api/employees/{id}/` - Update employee
- `DELETE /api/employees/{id}/` - Delete employee

### Attendance
- `GET /api/attendance/` - List attendance records
- `POST /api/attendance/` - Create attendance record
- `GET /api/attendance/{id}/` - Get attendance details
- `PUT /api/attendance/{id}/` - Update attendance
- `DELETE /api/attendance/{id}/` - Delete attendance

### Leaves
- `GET /api/leaves/` - List leave requests
- `POST /api/leaves/` - Create leave request
- `GET /api/leaves/{id}/` - Get leave details
- `PUT /api/leaves/{id}/` - Update leave
- `DELETE /api/leaves/{id}/` - Delete leave

### Payroll
- `GET /api/payroll/` - List payroll records
- `POST /api/payroll/` - Create payroll record
- `GET /api/payroll/{id}/` - Get payroll details
- `PUT /api/payroll/{id}/` - Update payroll
- `DELETE /api/payroll/{id}/` - Delete payroll

## Key Features Explained

### Pending Employees Workflow
1. New employee signs up via registration page
2. Employee profile created with status: "Pending"
3. Admin sees notification badge on "Pending Employees" button
4. Admin clicks button to view all pending employees
5. Admin configures employee details and activates account
6. Employee can now login and access their dashboard

### Role-Based Access Control
- **Admin**: Full access to all features and data
- **Employee**: Restricted access to personal data only
- Automatic redirection based on user role after login

### Token Authentication
- Secure API access using token-based authentication
- Tokens stored in localStorage
- Automatic token validation on protected routes
- No CSRF tokens required for API endpoints

### Currency Display
- All monetary values displayed in Philippine Peso (₱)
- Formatted with thousand separators for readability

## Development

### Database
- SQLite database: `db_auth.sqlite3`
- Migrations located in `employees/migrations/`
- Run migrations: `python manage.py migrate`

### Adding New Features
1. Update models in `employees/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update serializers in `employees/serializers.py`
5. Update views in `employees/views.py`
6. Update frontend JavaScript as needed

### Static Files
- Located in `frontend/static/`
- Served directly by Django during development
- Configure `STATIC_ROOT` for production deployment

## Troubleshooting

### Cannot login or register (403 error)
- Ensure Django server is running
- Check that `SessionAuthentication` is removed from REST_FRAMEWORK settings
- Clear browser cache and cookies

### Pending employees not showing
- Check that employee status is "Pending" in database
- Verify `admin_extensions.js` is loaded
- Check browser console for JavaScript errors

### Virtual environment issues
- Delete `alp` folder and run `setup.bat` again
- Ensure Python is in system PATH
- Try running commands manually

## Security Notes

- Change default admin password in production
- Use environment variables for sensitive settings
- Enable HTTPS in production
- Set `DEBUG = False` in production
- Configure proper `ALLOWED_HOSTS` in production
- Use PostgreSQL or MySQL in production (not SQLite)

## License

This project is for educational and internal use.

## Support

For issues or questions, contact the development team.

---

**Version**: 1.0  
**Last Updated**: February 22, 2026  
**Status**: Production Ready
