from sqlalchemy.orm import Session
from app.db.models import Session as UserSession
from uuid import UUID


class SessionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, session: UserSession) -> UserSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: UUID) -> UserSession | None:
        return self.db.query(UserSession).filter(UserSession.id == session_id).first()

    def delete(self, session: UserSession):
        self.db.delete(session)
        self.db.commit()

    def delete_all_for_user(self, user_id: UUID):
        self.db.query(UserSession).filter(UserSession.user_id == user_id).delete()
        self.db.commit()