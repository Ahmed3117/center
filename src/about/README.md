# About App

This app provides information about the platform, including about page content, features, and team members.

## Models

1. **AboutPage** - Contains the main content for the about page
2. **Feature** - Represents features or highlights to be displayed on the about page

## API Endpoints

### Public Endpoints

These endpoints are accessible without authentication:

- `GET /about/info/` - Get the about page content and all features
  - Returns the about page title, content, and a list of all features

- `GET /about/teachers/` - Get a list of all teachers
  - Returns information about teachers to be displayed on the home page

## Data Structure

### AboutPage with Features Response

```json
{
  "id": 1,
  "title": "About Our Platform",
  "content": "Detailed content about the platform...",
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-02T14:30:00Z",
  "features": [
    {
      "id": 1,
      "title": "Feature 1",
      "description": "Description of feature 1",
      "image": "http://example.com/media/features/feature1.jpg",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    {
      "id": 2,
      "title": "Feature 2",
      "description": "Description of feature 2",
      "image": "http://example.com/media/features/feature2.jpg",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    }
  ]
}
```

### Teachers Response

```json
[
  {
    "id": 1,
    "name": "Teacher Name",
    "specialization": "Subject",
    "description": "Teacher bio...",
    "image": "http://example.com/media/teachers/teacher1.jpg",
    "created_at": "2023-06-01T12:00:00Z",
    "updated_at": "2023-06-01T12:00:00Z"
  }
]
```

## API Endpoints

- `GET /api/about/pages/` - List all about pages
- `POST /api/about/pages/` - Create an about page (auth required)
- `GET /api/about/pages/<id>/` - Get a specific about page
- `PUT /api/about/pages/<id>/` - Update an about page (auth required)
- `DELETE /api/about/pages/<id>/` - Delete an about page (auth required)

- `GET /api/about/team/` - List all team members
- `POST /api/about/team/` - Create a team member (auth required)
- `GET /api/about/team/<id>/` - Get a specific team member
- `PUT /api/about/team/<id>/` - Update a team member (auth required)
- `DELETE /api/about/team/<id>/` - Delete a team member (auth required)

Note: Read operations are available to anyone, but create/update/delete operations require authentication. 