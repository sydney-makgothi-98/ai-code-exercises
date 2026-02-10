from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Callable, Optional, Type, TypeVar, Generic, List, Dict, Any
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Database models and session setup (simplified)
class Base:
    pass

class User(Base):
    __tablename__ = "users"
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool

class ActionLog(Base):
    __tablename__ = "action_logs"
    id: int
    user_id: int
    action: str
    details: Optional[str]
    created_at: datetime

# Type variable for repository generic
T = TypeVar('T', bound=Base)

# Generic repository pattern implementation
class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[T]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: T) -> T:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    # Additional CRUD methods...

# User repository (specialization of the generic repository)
class UserRepository(Repository[User]):
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

class ActionLogRepository(Repository[ActionLog]):
    pass

# Dependency injection for database session
async def get_db() -> AsyncSession:
    async with AsyncSession() as session:
        try:
            yield session
        finally:
            await session.close()

def get_action_log_service() -> ActionLogService:
    return ActionLogService(ActionLogRepository(ActionLog))

# Service layer
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_username(db, username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # Password verification logic
        return True  # Simplified for example

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")

class ActionLogService:
    def __init__(self, repository: ActionLogRepository):
        self.repository = repository

    async def log_action(
        self,
        db: AsyncSession,
        user_id: int,
        action: str,
        details: Optional[str] = None,
    ) -> ActionLog:
        log = ActionLog()
        log.user_id = user_id
        log.action = action
        log.details = details
        log.created_at = datetime.utcnow()
        return await self.repository.create(db, log)

# Middleware for tracking request timing
class TimingMiddleware:
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = datetime.utcnow()
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Dependency for getting current authenticated user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo = UserRepository(User)
    user = await user_repo.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

# Role-based access control decorator
def requires_role(role: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
            action_log_service: ActionLogService = Depends(get_action_log_service),
            **kwargs,
        ):
            if role == "admin" and not current_user.is_superuser:
                await action_log_service.log_action(
                    db,
                    user_id=current_user.id,
                    action="admin_forbidden",
                    details="Insufficient permissions",
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Application startup")
    yield
    # Shutdown logic
    print("Application shutdown")

# FastAPI application instance
app = FastAPI(lifespan=lifespan)
app.add_middleware(TimingMiddleware)

# Schema for user data
class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True

# API endpoints
@app.post("/token")
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db),
    action_log_service: ActionLogService = Depends(get_action_log_service),
):
    user_repo = UserRepository(User)
    user_service = UserService(user_repo)
    user = await user_service.authenticate_user(db, username, password)
    if not user:
        await action_log_service.log_action(
            db,
            user_id=0,
            action="login_failed",
            details=f"username={username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_service.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    await action_log_service.log_action(
        db,
        user_id=user.id,
        action="login",
        details="User login",
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin/users/", response_model=List[UserSchema])
@requires_role("admin")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    action_log_service: ActionLogService = Depends(get_action_log_service),
):
    user_repo = UserRepository(User)
    users = await user_repo.list(db, skip=skip, limit=limit)
    await action_log_service.log_action(
        db,
        user_id=current_user.id,
        action="admin_list_users",
        details=f"skip={skip}, limit={limit}",
    )
    return users