# Accounts App

This app manages user authentication and profiles. It includes:

- Custom User Model with additional fields:
  - Bio
  - Profile Picture
  - Date of Birth

## API Endpoints

- `GET /api/accounts/profiles/` - List all user profiles
- `POST /api/accounts/profiles/` - Create a user profile
- `GET /api/accounts/profiles/<id>/` - Get a specific user profile
- `PUT /api/accounts/profiles/<id>/` - Update a user profile
- `DELETE /api/accounts/profiles/<id>/` - Delete a user profile

Note: Most operations require authentication, but user creation (registration) is open to all. 