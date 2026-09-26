from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


bearer_scheme = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
