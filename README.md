# Project Template and Optional Features

This project was created using https://github.com/zagaran/django-template

See the readme on [django-template](https://github.com/zagaran/django-template) for:
* Instructions on starting your own project
* An explanation of included features.

# Local Project Setup

Set up a Python virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

```bash
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values.
nano config/.env

# Install pip requirements.
pip install --upgrade pip
pip install -r requirements-dev.txt

# Apply migrations and sync database schema.
python manage.py migrate
```

To run the project:
```bash
python manage.py runserver_plus
```

To access the database:
```bash
python manage.py shell_plus
```

To run the test suite:
```bash
python manage.py test
```

To get a test coverage report:
```bash
coverage run --source='.' manage.py test; coverage report
```

# Requirements

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to manage requirements.  In addition, it has two requirements files:

* `requirements.txt`: this is for requirements that should be installed on servers.
* `requirements-dev.txt`: this is a superset of requirements.txt that should be used only for local development.  This includes tools that are not needed on server deployments of the codebase and thus omitted in `requirements.txt` to reduce extraneous server installs.

To add a new dependency to or update requirements, add the entry to requirements.in (if it's needed for the codebase to run) or requirements-dev.in (if it's just needed for development) and run `pip-compile` to generate new .txt files:
```bash
nano requirements.in  # Updating Python dependencies as needed
nano requirements-dev.in  # Updating Python dev dependencies as needed
pip-compile requirements.in --upgrade  # Generate requirements.txt with updated dependencies
pip-compile requirements-dev.in --upgrade  # Generate requirements-dev.txt with updated dependencies
```

# Settings

This project uses [django-environ](https://django-environ.readthedocs.io/en/latest/)
to read configuration from either `config/.env` (for local development)
or from environment varables (for server deployments).  For a list of settings,
see the `environ.Env(` object in [config/settings.py](config/settings.py).