import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.db.models import User, Session as UserSession
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
# from app.cache.redis import redis_client


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    def register(self, email: str, password: str) -> User:
        if self.user_repo.get_by_email(email):
            raise ValueError("User already exists")

        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            role="USER",
            is_active=True,
        )

        return self.user_repo.create(user)

    def login(self, email: str, password: str, user_agent: str, ip: str) -> tuple[str, str]:

        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        session_id = uuid.uuid4()

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role,
            session_id=str(session_id),
        )

        refresh_token = create_refresh_token(
            user_id=str(user.id),
            session_id=str(session_id),
        )

        session = UserSession(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=hash_password(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            user_agent=user_agent,
            ip_address=ip,
        )

        self.session_repo.create(session)

        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token) 

        session_id = payload["session_id"]
        user_id = payload["sub"]

        session = self.session_repo.get_by_id(session_id)

        if not session:
            raise ValueError("Session not found")

        if not verify_password(refresh_token, session.refresh_token_hash):
            raise ValueError("Invalid refresh token")

        redis_client.setex(
            f"blacklist:{payload['jti']}",
            60 * 60 * 24 * 7,
            "true"
        )

        new_access = create_access_token(
            user_id=user_id,
            role="USER",
            session_id=session_id,
        )

        new_refresh = create_refresh_token(
            user_id=user_id,
            session_id=session_id,
        )

        session.refresh_token_hash = hash_password(new_refresh)
        self.db.commit()

        return new_access, new_refresh

    def logout(self, session_id: str):

        session = self.session_repo.get_by_id(session_id)
        if not session:
            return

        self.session_repo.delete(session)

    def logout_all(self, user_id: str):
        self.session_repo.delete_all_for_user(user_id)