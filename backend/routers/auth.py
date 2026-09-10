import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, User
from auth_utils import verify_password, get_password_hash, create_access_token, decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "customer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None = None
    role: str

class ProfileUpdate(BaseModel):
    name: str | None = None
    old_password: str | None = None
    new_password: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, role=user.role)
    
    # First user is admin, others are customers (fallback if role isn't explicitly set to admin)
    if user.role != "admin":
        stmt_count = select(User)
        result_count = await db.execute(stmt_count)
        if not result_count.scalars().first():
            new_user.role = "admin"
        
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(id=new_user.id, email=new_user.email, name=new_user.name, role=new_user.role)

@router.put("/profile", response_model=UserResponse)
async def update_profile(profile_data: ProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if profile_data.name is not None:
        current_user.name = profile_data.name
        
    if profile_data.new_password:
        if not profile_data.old_password:
            raise HTTPException(status_code=400, detail="Old password is required to set a new password")
        if not verify_password(profile_data.old_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect old password")
            
        current_user.hashed_password = get_password_hash(profile_data.new_password)
        
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name, role=current_user.role)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role}}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name, role=current_user.role)
