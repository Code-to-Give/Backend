import base64
import jwt
import os

from fastapi import HTTPException, status


ALGORITHM = "RS256"
JWT_PUBLIC_KEY = base64.b64decode(os.getenv("JWT_PUBLIC_KEY")).decode('utf-8')


async def get_current_user(token: str):
    """
    Retrieve the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY,
                             algorithms=[ALGORITHM])

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
