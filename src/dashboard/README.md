# Dashboard App

This app provides administrative dashboard functionality through REST API endpoints for managing core entities in the system.

## Models Managed

This app does not define its own models but provides API endpoints for:

1. **Year** model (from the accounts app)
2. **TypeEducation** model (from the accounts app)
3. **Teacher** model (from the accounts app)
4. **AboutPage** model (from the about app)
5. **Feature** model (from the about app)

## API Endpoints

### Year Endpoints

- `GET /dashboard/years/` - List all years
- `POST /dashboard/years/` - Create a new year
- `GET /dashboard/years/<id>/` - Get a specific year
- `PUT /dashboard/years/<id>/` - Update a year
- `DELETE /dashboard/years/<id>/` - Delete a year

### TypeEducation Endpoints

- `GET /dashboard/education-types/` - List all education types
- `POST /dashboard/education-types/` - Create a new education type
- `GET /dashboard/education-types/<id>/` - Get a specific education type
- `PUT /dashboard/education-types/<id>/` - Update an education type
- `DELETE /dashboard/education-types/<id>/` - Delete an education type

### Teacher Endpoints

- `GET /dashboard/teachers/` - List all teachers
- `POST /dashboard/teachers/` - Create a new teacher
- `GET /dashboard/teachers/<id>/` - Get a specific teacher
- `PUT /dashboard/teachers/<id>/` - Update a teacher
- `DELETE /dashboard/teachers/<id>/` - Delete a teacher

### AboutPage Endpoints

- `GET /dashboard/about-page/` - Get the about page content
- `POST /dashboard/about-page/` - Create or update the about page content
- `PUT /dashboard/about-page/` - Update the about page content
- `DELETE /dashboard/about-page/` - Delete the about page content

The AboutPage model is limited to a single instance. If an instance already exists, the POST and PUT methods will update the existing instance rather than creating a new one.

### Feature Endpoints

- `GET /dashboard/features/` - List all features
- `POST /dashboard/features/` - Create a new feature
- `GET /dashboard/features/<id>/` - Get a specific feature
- `PUT /dashboard/features/<id>/` - Update a feature
- `DELETE /dashboard/features/<id>/` - Delete a feature

## Authentication

All endpoints require authentication. Use the authentication method configured in the project (JWT Authentication). 