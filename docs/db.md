# Database Design

1. Users Table
- id (INT, PRIMARY KEY)
- username (VARCHAR)
- email (VARCHAR)
- password_hash (VARCHAR)
- created_at (DATETIME)
- updated_at (DATETIME)

2. Events Table
- id (INT, PRIMARY KEY)
- name (VARCHAR)
- description (TEXT)
- start_date (DATETIME)
- end_date (DATETIME)
- created_by (INT, FOREIGN KEY to Users table)
- created_at (DATETIME)
- updated_at (DATETIME)

3. EventData Table
- id (INT, PRIMARY KEY)
- event_id (INT, FOREIGN KEY to Events table)
- data (JSON or TEXT)
- timestamp (DATETIME)
- created_by (INT, FOREIGN KEY to Users table)
- created_at (DATETIME)
- updated_at (DATETIME)

4. Alerts Table
- id (INT, PRIMARY KEY)
- user_id (INT, FOREIGN KEY to Users table)
- event_id (INT, FOREIGN KEY to Events table)
- condition (JSON or TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)

5. Reports Table
- id (INT, PRIMARY KEY)
- user_id (INT, FOREIGN KEY to Users table)
- event_id (INT, FOREIGN KEY to Events table)
- filters (JSON or TEXT)
- format (VARCHAR)
- created_at (DATETIME)
- updated_at (DATETIME)

6. Notifications Table
- id (INT, PRIMARY KEY)
- user_id (INT, FOREIGN KEY to Users table)
- event_id (INT, FOREIGN KEY to Events table)
- message (TEXT)
- read_status (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
