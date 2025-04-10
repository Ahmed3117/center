# Courses App

This app manages course-related functionality, including courses, course groups, and course scheduling.

## Models

1. **Course** - Represents a course offering with a title, year, and education type
2. **CourseGroup** - Represents a group within a course, taught by a specific teacher
3. **CourseGroupTime** - Represents the scheduling of a course group (day and time)

## API Endpoints

### Public Endpoints

These endpoints are accessible without authentication:

- `GET /courses/courses/` - List all courses
  - Optional query parameters:
    - `year`: Filter by year ID
    - `type_education`: Filter by education type ID

- `GET /courses/course-groups/` - List all course groups with their schedules
  - Optional query parameters:
    - `course`: Filter by course ID
    - `teacher`: Filter by teacher ID

## Data Structure

### Courses Response

```json
[
  {
    "id": 1,
    "title": "Mathematics",
    "year_name": "First Year",
    "type_education_name": "High School",
    "created_at": "2023-06-01T12:00:00Z",
    "updated_at": "2023-06-01T12:00:00Z"
  }
]
```

### Course Groups Response

```json
[
  {
    "id": 1,
    "course": {
      "id": 1,
      "title": "Mathematics",
      "year_name": "First Year",
      "type_education_name": "High School",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    "teacher": {
      "id": 1,
      "name": "Teacher Name",
      "specialization": "Mathematics",
      "description": "Teacher bio...",
      "image": "http://example.com/media/teachers/teacher1.jpg",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z"
    },
    "times": [
      {
        "id": 1,
        "day": 1,
        "day_display": "Monday",
        "time": 1.5,
        "created_at": "2023-06-01T12:00:00Z",
        "updated_at": "2023-06-01T12:00:00Z"
      },
      {
        "id": 2,
        "day": 3,
        "day_display": "Wednesday",
        "time": 1.5,
        "created_at": "2023-06-01T12:00:00Z",
        "updated_at": "2023-06-01T12:00:00Z"
      }
    ],
    "created_at": "2023-06-01T12:00:00Z",
    "updated_at": "2023-06-01T12:00:00Z"
  }
]
``` 