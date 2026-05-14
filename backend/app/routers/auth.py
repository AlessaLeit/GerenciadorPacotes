from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.auth import ADMIN_EMAIL, ADMIN_PASSWORD, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_data: LoginRequest):
    """
    Endpoint de login que valida se o e-mail está na lista permitida.
    """
    if not login_data.username or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail e senha são obrigatórios"
        )

    email = login_data.username.lower()
    
    if email != ADMIN_EMAIL or login_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token JWT
    access_token = create_access_token(data={"sub": email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"email": email}
    }