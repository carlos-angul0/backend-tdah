from datetime import datetime, timedelta
from jose import JWTError, jwt # Librería para manejar JSON Web Tokens (JWT)
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import UsuarioDB


# Constantes para la generación de tokens JWT
SECRET_KEY = "tdah_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Esquema de autenticación OAuth2 con contraseña
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


#Función para crear un token de acceso
def crear_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

# Función para verificar el token de acceso
def verificar_token(token: str):

    try:
        infoToken = jwt.decode( # Información interna del token
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = infoToken.get("sub")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        return email

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

# Función para obtener el usuario actual a partir del token de acceso 
def get_usuario_actual(
    token: str = Depends(oauth2_scheme)
):
    email = verificar_token(token)
    db = SessionLocal()

    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.email == email
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return usuario


# Función para verificar que el usuario actual es admin
def only_admin(
    usario_actual: UsuarioDB = Depends(get_usuario_actual)
):

    if usario_actual.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos"
        )
    
    return usario_actual