# Django REST Framework Project

This is a Django REST Framework project with the following structure:
- Main project: `core`
- Apps: `accounts`, `about`

## Setup

1. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Apply migrations:
```
python manage.py migrate
```

4. Run the development server:
```
python manage.py runserver
```

## Project Structure
- `core/`: Main project settings
- `accounts/`: User authentication and management
- `about/`: About page and information 