# Flask Boilerplate

## Getting Started

### Prerequisites

- Python version: `> python 3.12.0`
- Flask version: `3.1.3`
- Database: `postgresql`

## Installation

- Clone the repository: `git clone https://github.com/GoldenOwlAsia/python-flask-api-template.git`
- Initalize virtual environment: `python3 -m venv env`
- Activate virtual environment: `source env/bin/activate`
- Go to python-flask-api-template folder: `cd ./python-flask-api-template`
- Install the dependencies: `pip install -r requirements.txt`
- Create `instance/config.py` (a random `SECRET_KEY` and your database URI) and `.env`: `python configure.py`. The app refuses to start without a `SECRET_KEY`.
- `.env` looks like this. `APP_CONFIG` defaults to `production` when unset:
```
FLASK_DEBUG=1 or 0
APP_CONFIG=development or production
FLASK_RUN_PORT=5000
FLASK_SENTRY_ENABLED=false
FLASK_SENTRY_DSN=
```
- Create database by docker command: `docker run --name flask -p 5435:5432 -e POSTGRES_PASSWORD=flask -e POSTGRES_USER=flask -e POSTGRES_DB=flask -d postgres:14`
- Turn to line 63 in `alembic.ini` file, change the value follows this structure : postgresql://POSTGRES_USER:POSTGRES_PASSWORD@POSTGRES_HOST:POSTGRES_PORT/POSTGRES_DB
- Run migration: `alembic upgrade head`
- Export env :
    -   `export FLASK_APP=app/app.py`
- Run application: `flask run --no-debugger --no-reload`
- Visit `http://127.0.0.1:5000` and start your development

## Testing

- python3 -m unittest

## Database diagram

![Database diagram](db_diagram.png)
