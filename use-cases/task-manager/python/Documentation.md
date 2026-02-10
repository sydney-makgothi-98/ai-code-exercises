CODE DOCUMENTATION

Using Prompt 1. I asked the LLM to create comprehensive documentation for the entire CLI project. It did so via docstring addition through every class and every method in the entire codebase. The function of interest to me was the task score function: 

def calculate_task_score(task)

The doc string outlines the prupose of the function quite nicely, its inputs and the expected outputs, and how the priority scores can be varied within the function to suit my and my teams needs. 

Prompt 2 

I used it to help me better understand algo.py, at a high level this file is score ranking algorthim, defined as a UDF (User Defined Function) which allows it to be used for different cases and situtions. 

The function uses a score to place importance/urgency on a task. The higher the score, the higher the urgency of the task. 

One of the edge cases or boundary conditions has to with timezones. Algo.py uses datetime.now() for time comparisons, which can be problematic if the time stamps are UTC.

API DOCUMENTATION

Prompts 1 to 3 

Were used to create the documentation below. I am only currently learning about APIs so I cannoy say with 100% confidence I know exactly what is going on here. 

However the most important takeaway it took from these prompts, was that AI can create a dev-brief for you. Which is actually what I need when developing Django apps, because most clients are really bad at describing the problems they are facing.

Product API - User Registration Endpoint

Purpose
Create a new user account, validate input, store the user in the database, and return the created user record (without the password). A confirmation token is generated and a confirmation email is attempted (logged only in the current implementation).

Endpoint
POST /api/users/register

Authentication
None. This endpoint is public.

Request Parameters
Path parameters: None
Query parameters: None
Body (JSON):
- username (string, required): Desired username. Must be unique.
- email (string, required): User email. Must be valid format and unique.
- password (string, required): Raw password. Must be at least 8 characters.

Response Format
Content-Type: application/json

Success Responses
201 Created
{
	"message": "User registered successfully",
	"user": {
		"id": 1,
		"username": "jdoe",
		"email": "jdoe@example.com",
		"created_at": "2026-01-28T12:34:56.789123",
		"role": "user"
	}
}

Error Responses
400 Bad Request
- Missing required field
{
	"error": "Missing required field",
	"message": "username is required"
}

400 Bad Request
- Invalid email
{
	"error": "Invalid email",
	"message": "Please provide a valid email address"
}

400 Bad Request
- Weak password
{
	"error": "Weak password",
	"message": "Password must be at least 8 characters long"
}

409 Conflict
- Username taken
{
	"error": "Username taken",
	"message": "Username is already in use"
}

409 Conflict
- Email exists
{
	"error": "Email exists",
	"message": "An account with this email already exists"
}

500 Internal Server Error
{
	"error": "Server error",
	"message": "Failed to register user"
}

Example Requests
Example 1
Request
POST /api/users/register
{
	"username": "jdoe",
	"email": "jdoe@example.com",
	"password": "S3curePass!"
}

Response (201)
{
	"message": "User registered successfully",
	"user": {
		"id": 1,
		"username": "jdoe",
		"email": "jdoe@example.com",
		"created_at": "2026-01-28T12:34:56.789123",
		"role": "user"
	}
}

Example 2
Request
POST /api/users/register
{
	"username": "jdoe",
	"email": "bad-email",
	"password": "short"
}

Response (400)
{
	"error": "Invalid email",
	"message": "Please provide a valid email address"
}

Rate Limiting / Special Considerations
- No rate limiting is currently implemented.
- Uses local time via datetime.utcnow() for created_at.
- Email sending is a placeholder that logs the action; no external email service is configured.
- Database defaults to SQLite if DATABASE_URL is not set.

Developer Guide (Python/Flask)

Audience and tone
This guide is for inexperienced developers who may lean heavily on AI. It aims to be friendly, clear, and practical, helping you understand what the API expects and how to troubleshoot.

1. Authentication
This endpoint does not require authentication. You can call it directly without API keys or tokens.

2. Properly format requests
Endpoint: POST /api/users/register
Content-Type: application/json

Required JSON body fields:
- username (string): Must be unique
- email (string): Must be valid email format and unique
- password (string): At least 8 characters

Tips:
- Always send JSON (not form data).
- Match field names exactly: username, email, password.
- Use a real email format like name@example.com.

3. Handle and interpret responses
Success (201): You get a user object without a password.
Errors: You get a JSON response with error and message fields.
Use the HTTP status code first, then read the message for the next action.

4. Common errors and how to fix them
- 400 Missing required field: Add the missing field to your JSON.
- 400 Invalid email: Fix the email format.
- 400 Weak password: Use a password with 8+ characters.
- 409 Username taken: Choose a different username.
- 409 Email exists: Use a different email.
- 500 Server error: Try again later and check server logs.

5. Example code (Python + Flask test client)
Below is a minimal example using Flask's test client to call the API locally.

Example: Successful registration
from product_API import app

with app.test_client() as client:
	response = client.post(
		"/api/users/register",
		json={
			"username": "jdoe",
			"email": "jdoe@example.com",
			"password": "S3curePass!"
		}
	)
	print(response.status_code)
	print(response.get_json())

Example: Invalid email
from product_API import app

with app.test_client() as client:
	response = client.post(
		"/api/users/register",
		json={
			"username": "jdoe",
			"email": "bad-email",
			"password": "shortpass"
		}
	)
	print(response.status_code)
	print(response.get_json())

Special considerations
- No rate limiting is enforced right now.
- Email sending is a placeholder that logs to the server console.
- The database defaults to SQLite if DATABASE_URL is not set.

PROJECT README (Generated)

Title
Task Manager + Product API (Python)

Overview
This project includes a simple task manager CLI and a minimal Flask API endpoint for user registration. It is intended for learning, experimentation, and small demos.

Key Features
- Task CRUD operations and priority scoring
- JSON file persistence for tasks
- User registration endpoint with validation
- SQLite database by default for the API

Project Structure
- app.py: TaskManager application layer
- cli.py: CLI entry point
- models.py: Task and enums
- storage.py: JSON persistence
- algo.py: Task scoring/ranking helpers
- product_API.py: Flask registration endpoint
- openapi.yaml: OpenAPI spec for the registration endpoint

Requirements
- Python 3.13+
- Flask, Flask-SQLAlchemy, Werkzeug, itsdangerous

Quick Start
1) Create and activate a virtual environment
2) Install dependencies
3) Run the API: python product_API.py
4) Use the CLI: python cli.py --help

Configuration
- DATABASE_URL: SQLAlchemy database URL (optional)
- SECRET_KEY: Secret key for token generation (optional)

Known Limitations
- No auth on the registration endpoint
- No rate limiting
- Email sending is a placeholder

License
Educational/demo use

STEP-BY-STEP GUIDE (Generated)

Goal
Get the API and CLI running locally.

Step 1: Create a virtual environment
- Use Python’s venv to isolate dependencies.

Step 2: Install dependencies
- Install Flask, Flask-SQLAlchemy, Werkzeug, and itsdangerous.

Step 3: Run the API
- Run product_API.py
- The app will create a SQLite database file if none exists.

Step 4: Test the API
- Send a POST request to /api/users/register with JSON.

Step 5: Use the CLI
- Run cli.py with commands like create, list, status, priority.

Step 6: Review logs and data
- API logs appear in the console.
- Task data is saved to tasks.json by default.

FAQ (Generated)

Q: Do I need authentication to call the registration endpoint?
A: No. It is public.

Q: Where is the user data stored?
A: In SQLite (users.db) by default, or in the database pointed to by DATABASE_URL.

Q: Why am I getting “Invalid email” errors?
A: The email must match a basic regex pattern and include @ and a domain.

Q: Why do I see a 409 conflict?
A: The username or email is already in the database.

Q: How do I reset the API database?
A: Delete users.db and restart the app to recreate tables.

Q: Why aren’t emails sending?
A: The email function is a placeholder that only logs to the console.

Q: Where are tasks stored?
A: In tasks.json by default.

Q: How do I change the database location?
A: Set DATABASE_URL in your environment before running product_API.py.
