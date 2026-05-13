from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Hashear contraseña
def hash_password(password: str):
    return pwd_context.hash(password)

# Verificar contraseña
def verificar_password(usuario_password, hashed_password):
    return pwd_context.verify(usuario_password, hashed_password)