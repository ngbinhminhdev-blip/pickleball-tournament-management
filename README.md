# Pickleball Tournament Management System

A web-based application for managing Pickleball tournaments, developed with Flask. The system helps organizers manage tournaments, players, and match schedules through a simple web interface.

## Features

- Create and manage Pickleball tournaments
- Register players for tournaments
- Manage tournament participants
- Generate and manage match schedules
- Record Best-of-3 match scores
- Display tournament information dynamically using Jinja2 templates

## Technologies

- Python
- Flask
- Jinja2
- HTML
- CSS
- SQLite
- Git

## Project Structure

```
├── app.py
├── init_db.py
├── manager.py
├── upgrade_db.py
├── static/
├── templates/
└── README.md
```

## Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/pickleball-tournament-management.git
```

2. Install dependencies

```bash
pip install flask
```

3. Initialize the database

```bash
python init_db.py
```

4. Run the application

```bash
python app.py
```

5. Open your browser and visit:

```
http://127.0.0.1:5000
```

## Project Status

🚧 **In Progress**

Current progress:
- Tournament management
- Player management
- Match management
- Database design
- Ongoing frontend improvements

## Future Improvements

- User authentication
- Automatic match scheduling
- Tournament brackets
- Statistics dashboard
- Responsive UI

## Author

**Minh Nguyen**
