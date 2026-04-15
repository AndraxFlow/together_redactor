from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.core.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY
from app.db.session import engine
from app.models.users import users


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _resolve_engine(db_engine: Optional[Engine]) -> Engine:
    return db_engine or engine


def get_user_by_email(email: str, db_engine: Optional[Engine] = None) -> Optional[dict]:
    current_engine = _resolve_engine(db_engine)
    with current_engine.connect() as connection:
        result = connection.execute(select(users).where(users.c.email == email)).mappings().first()
        return dict(result) if result else None


def get_user_by_id(user_id: int, db_engine: Optional[Engine] = None) -> Optional[dict]:
    current_engine = _resolve_engine(db_engine)
    with current_engine.connect() as connection:
        result = connection.execute(select(users).where(users.c.id == user_id)).mappings().first()
        return dict(result) if result else None


def create_user(email: str, password: str, db_engine: Optional[Engine] = None) -> dict:
    current_engine = _resolve_engine(db_engine)
    payload = {"email": email, "hashed_password": hash_password(password)}
    query = users.insert().values(**payload).returning(users.c.id, users.c.email)
    try:
        with current_engine.begin() as connection:
            created_user = connection.execute(query).mappings().first()
    except IntegrityError as exc:
        raise ValueError(f"User with this email already exists {exc}") from exc
    return dict(created_user)


def authenticate_user(email: str, password: str, db_engine: Optional[Engine] = None) -> Optional[dict]:
    user = get_user_by_email(email, db_engine=db_engine)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_token(user_id: int) -> str:
    return create_access_token({"sub": str(user_id)})
