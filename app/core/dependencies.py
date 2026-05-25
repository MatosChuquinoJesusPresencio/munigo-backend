from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings, RolUsuario
from app.core.security import decode_access_token


security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    token: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> Optional[Dict[str, Any]]:
    token_str = None
    
    if token:
        token_str = token.credentials
    elif access_token:
        token_str = access_token
    
    if not token_str:
        return None
    
    payload = decode_access_token(token_str)
    if not payload:
        return None
    
    sub = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")
    
    if sub is None or email is None or role is None:
        return None
    
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        return None
    
    return {
        "user_id": user_id,
        "email": email,
        "role": role
    }


async def get_current_user_or_401(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


def require_role(*required_roles: RolUsuario):
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user_or_401)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        role_values = [role.value for role in required_roles]
        if user_role not in role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes"
            )
        return current_user
    return role_checker


get_current_ciudadano = require_role(RolUsuario.CIUDADANO)
get_current_funcionario = require_role(RolUsuario.FUNCIONARIO)
get_current_inspector = require_role(RolUsuario.INSPECTOR)
get_current_gerente = require_role(RolUsuario.GERENTE)
