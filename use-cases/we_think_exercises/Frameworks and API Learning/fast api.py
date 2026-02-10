"""
FastAPI: Hello World + validation + error handling + project structure

Note: Python module names should not contain spaces. Consider renaming this file to
fast_api.py for the run commands below.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Create the FastAPI application instance.
app = FastAPI(title="Hello World API", version="1.0.0")


# Define a GET endpoint at the root path.
@app.get("/")
def read_root() -> dict:
		# Return JSON data; FastAPI handles serialization.
		return {"message": "Hello World"}


# Pydantic models declare and validate request bodies.
class UserCreate(BaseModel):
		name: str = Field(..., min_length=1, max_length=50)
		age: int = Field(..., ge=13, le=120)


class User(UserCreate):
		id: int


_fake_db: dict[int, User] = {}
_next_id = 1


# Create a user using a validated request body.
@app.post("/users", response_model=User, status_code=201)
def create_user(payload: UserCreate) -> User:
		global _next_id
		if payload.name.lower() == "admin":
				raise HTTPException(status_code=400, detail="'admin' is reserved.")

		user = User(id=_next_id, name=payload.name, age=payload.age)
		_fake_db[_next_id] = user
		_next_id += 1
		return user


# Fetch a user and return 404 if it does not exist.
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
		user = _fake_db.get(user_id)
		if not user:
				raise HTTPException(status_code=404, detail="User not found.")
		return user


# Example of custom error handling for domain errors.
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
		return JSONResponse(status_code=400, content={"detail": str(exc)})


"""
How to add request body validation with Pydantic
- Define a model that inherits from BaseModel.
- Use Field(...) to set constraints (min/max length, numeric bounds, etc.).
- FastAPI validates inputs automatically and returns 422 on invalid data.

Proper error handling in FastAPI
- Use HTTPException for expected HTTP errors (404, 400, 401).
- Add exception handlers for domain-specific errors with @app.exception_handler.
- Use response models to validate and shape error responses if needed.

Organizing a FastAPI project into multiple files/modules (example)

my_app/
	app/
		__init__.py
		main.py            # FastAPI app instance
		api/
			__init__.py
			routes.py        # APIRouter definitions
		models/
			__init__.py
			schemas.py       # Pydantic models
		services/
			__init__.py
			users.py         # Business logic
		core/
			__init__.py
			config.py        # Settings and env management
	tests/
		test_main.py
	pyproject.toml

Minimal multi-file wiring
app/api/routes.py:
	from fastapi import APIRouter
	router = APIRouter()
	@router.get("/health")
	def health():
			return {"status": "ok"}

app/main.py:
	from fastapi import FastAPI
	from app.api.routes import router
	app = FastAPI()
	app.include_router(router)

How to run locally (assuming the file is app/main.py)
1) Install dependencies:
	 pip install fastapi uvicorn
2) Run the dev server with auto-reload:
	 uvicorn app.main:app --reload
3) Open docs in the browser:
	 http://127.0.0.1:8000/docs

How to test locally (pytest + TestClient)
1) Install test dependency:
	 pip install pytest
2) Example test (tests/test_main.py):

	 from fastapi.testclient import TestClient
	 from app.main import app

	 client = TestClient(app)

	 def test_root():
			 response = client.get("/")
			 assert response.status_code == 200
			 assert response.json() == {"message": "Hello World"}

3) Run tests:
	 pytest
"""
