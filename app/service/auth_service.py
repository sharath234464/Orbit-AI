from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi import HTTPException, status

password_hash = PasswordHash.recommended()

class AuthService:
    def __init__(self, repository, settings):
        self.repository, self.settings = repository, settings

    def _user_out(self, record):
        return {"id": str(record["_id"]), "name": record["name"], "email": record["email"]}

    async def register(self, name, email, password):
        email = email.lower().strip()
        if await self.repository.find_by_email(email):
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        record = {"name": name.strip(), "email": email, "password_hash": password_hash.hash(password), "created_at": datetime.now(timezone.utc)}
        try:
            record = await self.repository.create_user(record)
        except Exception as exc:
            raise HTTPException(status_code=409, detail="Could not create account; the email may already be registered.") from exc
        return self._auth_response(record)

    async def login(self, email, password):
        record = await self.repository.find_by_email(email.lower().strip())
        if not record or not password_hash.verify(password, record["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
        return self._auth_response(record)

    def _auth_response(self, record):
        expiry = datetime.now(timezone.utc) + timedelta(minutes=self.settings.access_token_expire_minutes)
        token = jwt.encode({"sub": str(record["_id"]), "exp": expiry}, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
        return {"access_token": token, "token_type": "bearer", "user": self._user_out(record)}

    async def current_user(self, token):
        try:
            payload = jwt.decode(token, self.settings.jwt_secret_key, algorithms=[self.settings.jwt_algorithm])
            user_id = payload.get("sub")
            if not user_id: raise ValueError("Missing subject")
        except (JWTError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.") from exc
        user = await self.repository.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists.")
        return self._user_out(user)
