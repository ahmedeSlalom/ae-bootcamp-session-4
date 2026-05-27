# Slalom Capabilities Management API

<p align="center">
  <img src="./.images/byte-teacher.png" alt="Byte Teacher" width="200" />
</p>

A FastAPI application that enables Slalom consultants to register their capabilities and manage consulting expertise across the organization.

## Features

- View all available consulting capabilities
- Register consultant expertise and availability
- Track skill levels and certifications
- Manage capability capacity and team assignments

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc
   - Capabilities Dashboard: http://localhost:8000/

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/capabilities`                                                   | Get all capabilities with details and current consultant assignments |
| POST   | `/capabilities/{capability_name}/register?email=consultant@slalom.com` | Register consultant for a capability                     |
| DELETE | `/capabilities/{capability_name}/unregister?email=consultant@slalom.com` | Unregister consultant from a capability              |
| GET    | `/consultants`                                                    | Get the persisted consultant records and registrations              |
| GET    | `/consultants/export`                                             | Export all consultant records as JSON                              |
| POST   | `/consultants/import`                                             | Replace consultant records in bulk from JSON                       |

## Data Model

The application uses a consulting-focused data model:

1. **Capabilities** - Uses capability name as identifier:
   - Description of the consulting capability
   - Skill levels (Emerging, Proficient, Advanced, Expert)
   - Practice area (Strategy, Technology, Operations)
   - Industry verticals served
   - Required certifications
   - List of consultant emails registered
   - Available capacity (hours per week)
   - Geographic location preferences

2. **Consultants** - Uses email as identifier:
   - Name
   - Practice area
   - Skill level
   - Certifications
   - Availability

All data is currently stored in memory for this learning exercise. In a production environment, this would be backed by a robust database system.

## Consultant Persistence

Consultant records and capability registrations are now persisted to `src/data/consultants.json`.
If the file does not exist, the app creates it on startup from the seeded consultant registrations.

### Bulk Import Format

Use `POST /consultants/import` with a JSON payload shaped like this:

```json
{
   "consultants": [
      {
         "email": "jane.doe@slalom.com",
         "name": "Jane Doe",
         "practice_area": "Technology",
         "title": "Principal Consultant",
         "availability": 32,
         "certifications": ["AWS Solutions Architect"],
         "capability_registrations": ["Cloud Architecture", "DevOps Engineering"]
      }
   ]
}
```

The import validates duplicate emails, malformed email addresses, and unknown capabilities before replacing the stored consultant dataset.

### Export

Use `GET /consultants/export` to retrieve the full consultant dataset for reporting or downstream sync workflows.

## Future Enhancements

This exercise will guide you through implementing:
- Capability maturity assessments
- Intelligent team matching algorithms  
- Analytics dashboards for practice leads
- Integration with project management systems
- Advanced search and filtering capabilities
