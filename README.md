# Event Decision Tracker (EDT)

A comprehensive Django-based application for tracking events, decisions, and deliverables in project management.

## Features

- **Role-based Access Control**: Admin, Management User, and Project User roles
- **Project Management**: Create and manage projects with events
- **Event Tracking**: Schedule events with conflict detection
- **Decision Management**: Track decisions made during events
- **Deliverable Assignment**: Assign and track tasks from decisions
- **Invitation System**: Invite users to events with status tracking
- **Real-time Calendar**: FullCalendar.js integration with conflict detection
- **Progress Analytics**: Chart.js visualizations for progress tracking
- **Responsive UI**: Tailwind CSS for modern, responsive design

## Tech Stack

- **Backend**: Django 5.2.6 + Django REST Framework
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: SQLite (development) / MySQL (production)
- **JavaScript Libraries**: FullCalendar.js, Chart.js, Alpine.js
- **Icons**: Font Awesome

## User Roles

### Admin
- Full system control
- Manage all users, projects, events, decisions, and deliverables
- Access to Django Admin interface
- System-wide analytics and reports

### Management User
- Create and manage projects
- Create events and add agendas
- Make decisions and assign deliverables
- Link events for reference
- Project progress monitoring

### Project User
- Create events in projects they participate in
- Update their assigned deliverables
- View their dashboard with tasks and invitations
- Participate in events they're invited to

## Installation

### Prerequisites
- Python 3.13+
- pip (Python package manager)
- MySQL (for production) or SQLite (for development)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dicision_tracker
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install Django mysqlclient django-cors-headers djangorestframework pillow
   ```

4. **Database Configuration**:

   **For Development (SQLite - Default)**:
   The project is pre-configured to use SQLite for development. No additional setup needed.

   **For Production (MySQL)**:
   ```python
   # In dicision_tracker/settings.py, uncomment and configure:
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'decision_tracker_db',
           'USER': 'your_mysql_user',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   ```

   Create MySQL database:
   ```sql
   CREATE DATABASE decision_tracker_db;
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main application: http://127.0.0.1:8000/
   - Django Admin: http://127.0.0.1:8000/admin/

## Usage

### First Login
1. Access the application at http://127.0.0.1:8000/
2. Use the superuser credentials to login
3. The system will redirect you to the appropriate dashboard based on your role

### Creating Users
1. Admin users can create new users via the Django Admin interface
2. Or users can register themselves at /accounts/register/
3. Admin can update user roles via the user management interface

### Basic Workflow
1. **Admin/Management**: Create a project
2. **Management**: Create events within the project
3. **Management**: Add agenda items and invite participants
4. **During/After Event**: Record decisions made
5. **Management**: Assign deliverables to project users
6. **Project Users**: Update progress on their assigned deliverables

## Development Roadmap

### Phase 1: ✅ Completed
- Django setup and models
- User authentication with roles
- Basic dashboard views
- Tailwind CSS integration

### Phase 2: 🚧 In Progress
- CRUD operations for Projects, Events, Decisions
- Form handling and validation
- Enhanced UI components

### Phase 3: 📋 Planned
- FullCalendar.js integration
- Event conflict detection
- Invitation system with email notifications

### Phase 4: 📋 Planned
- Progress tracking and analytics
- Chart.js integration
- Advanced reporting features

### Phase 5: 📋 Planned
- Event linking system
- Advanced search and filtering
- Performance optimizations

## Project Structure

```
dicision_tracker/
├── accounts/                 # User management and authentication
├── core/                    # Main business logic (Projects, Events, etc.)
├── dashboard/               # Role-based dashboard views
├── templates/               # HTML templates
│   ├── accounts/           # Authentication templates
│   ├── dashboard/          # Dashboard templates
│   ├── admin_base.html     # Admin layout
│   ├── management_base.html # Management layout
│   ├── project_user_base.html # Project User layout
│   └── base.html           # Base template
├── static/                  # Static files (CSS, JS, images)
├── dicision_tracker/        # Django project settings
└── manage.py               # Django management script
```

## Database Schema

### Core Models
- **CustomUser**: Extended user model with roles
- **Project**: Container for events and activities
- **Event**: Meetings, sessions with agenda and participants
- **Decision**: Outcomes recorded during events
- **Deliverable**: Tasks assigned from decisions
- **Invitation**: Event invitation tracking
- **EventLink**: Links between related events

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team.