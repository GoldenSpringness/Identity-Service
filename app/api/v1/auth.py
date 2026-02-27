from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.db.session import get_db
from app.api.schemas import (
    RegisterSchema,
    LoginSchema,
    RefreshSchema,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        service.register(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "User created successfully"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        access, refresh = service.login(
            email=data.email,
            password=data.password,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshSchema, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        access, refresh = service.refresh(data.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout(current["session_id"])

    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout_all(str(current["user"].id))

    return {"message": "All sessions revoked"}


@router.get("/me")
def get_me(current=Depends(get_current_user)):
    user = current["user"]

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }