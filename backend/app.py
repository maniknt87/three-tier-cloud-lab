import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://cloudlab:CloudLabPass123!@db:3306/cloudlab",
)
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
password_hash = PasswordHash.recommended()

app = FastAPI(title="Three-Tier Cloud Lab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


def create_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "exp": expires},
        JWT_SECRET,
        algorithm="HS256",
    )


def get_current_user(authorization: str | None = None):
    # Kept simple for the lab; the endpoint below extracts the header directly.
    return authorization


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "healthy", "service": "backend", "database": "reachable"}


@app.post("/api/login")
def login(payload: LoginRequest):
    with SessionLocal() as db:
        row = db.execute(
            text(
                "SELECT id, username, password_hash, display_name, role "
                "FROM users WHERE username = :username"
            ),
            {"username": payload.username},
        ).mappings().first()

        if not row or not password_hash.verify(payload.password, row["password_hash"]):
            db.execute(
                text(
                    "INSERT INTO audit_events(username, event_type) "
                    "VALUES (:username, 'LOGIN_FAILED')"
                ),
                {"username": payload.username},
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        db.execute(
            text(
                "INSERT INTO audit_events(username, event_type) "
                "VALUES (:username, 'LOGIN_SUCCESS')"
            ),
            {"username": payload.username},
        )
        db.commit()

        return {
            "access_token": create_token(row["username"]),
            "token_type": "bearer",
            "user": {
                "username": row["username"],
                "display_name": row["display_name"],
                "role": row["role"],
            },
        }


def require_user(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/api/profile")
def profile(authorization: str | None = Header(default=None)):
    username = require_user(authorization or "")
    with SessionLocal() as db:
        row = db.execute(
            text(
                "SELECT username, display_name, role, created_at "
                "FROM users WHERE username = :username"
            ),
            {"username": username},
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "created_at": row["created_at"],
    }


@app.get("/api/stats")
def stats(authorization: str | None = Header(default=None)):
    username = require_user(authorization or "")
    with SessionLocal() as db:
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        total_logins = db.execute(
            text("SELECT COUNT(*) FROM audit_events WHERE event_type='LOGIN_SUCCESS'")
        ).scalar_one()

    return {
        "requested_by": username,
        "total_users": total_users,
        "successful_logins": total_logins,
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
    }
