from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum
from app.database import engine, SessionLocal
from app.models import Base, UsuarioDB
from sqlalchemy.orm import Session
from app.security import hash_password, verificar_password
from app.dependencies.auth import crear_access_token, get_usuario_actual, only_admin
from app.schemas import Usuario, UsuarioRespuesta, Login, UsuarioUpdate
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear instancia de FastAPI
app = FastAPI()


#<------ ENDPOINTS ------->

# Endpoint de prueba
@app.get("/")
def home():
    return {"message": "Backend TDAH funcionando 🚀"}

# LOGIN
@app.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.email == data.username
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    if not verificar_password(data.password, usuario.password):
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )

    token = crear_access_token(
        data={"sub": usuario.email, "rol": usuario.rol}
    )
    print("LOGIN EJECUTADO")
    print(data.username)
    print(data.password)
    print(token)

    return {
        # "message": "Login exitoso",
        # "usuario": usuario.email,
        # "rol": usuario.rol,
        "access_token": token,
        "token_type": "bearer"
    }

# GET - Obtener usuarios
@app.get("/usuarios",
         response_model=list[UsuarioRespuesta])
def obtener_usuarios(
    usuario_actual: str = Depends(only_admin),
    db: Session = Depends(get_db)
):
    usuarios = db.query(UsuarioDB).all()
    return usuarios



# POST - Crear usuario
@app.post("/usuarios",
          response_model=UsuarioRespuesta)
def registrar_usuario(
    user: Usuario,
    usuario_actual: str = Depends(only_admin), 
    db: Session = Depends(get_db)):
    
    # Verificar si el email ya está registrado
    usuario_existente = db.query(UsuarioDB).filter(
    UsuarioDB.email == user.email
    ).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario con contraseña hasheada
    nuevo_usuario = UsuarioDB(
        nombre=user.nombre,
        apellido=user.apellido,
        fecha_nacimiento=user.fecha_nacimiento,
        email=user.email,
        telefono=user.telefono,
        rol=user.rol,
        password=hash_password(user.password)
    )

    db.add(nuevo_usuario)

    try:
        db.commit()
        db.refresh(nuevo_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )

    return nuevo_usuario

# PUT - Actualizar usuario
@app.put("/usuarios/{user_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(
    user_id: int,
    user: UsuarioUpdate,
    usuario_actual = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
    ):

    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.id == user_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    
    usuario.nombre = user.nombre
    usuario.apellido = user.apellido
    usuario.fecha_nacimiento = user.fecha_nacimiento
    usuario.telefono = user.telefono
    # Solo el admin puede cambiar el rol de un usuario
    if usuario_actual.rol != "admin":
        
        if user.rol != usuario.rol:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para cambiar el rol del usuario"
            )
    usuario.rol = user.rol

    db.commit()
    db.refresh(usuario)
    return usuario

# DELETE - Eliminar usuario
@app.delete("/usuarios/{user_id}")
def eliminar_usuario(
    user_id: int,
    usuario_actual: str = Depends(only_admin),
    db: Session = Depends(get_db)
):

    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.id == user_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario.activo = False

    db.commit()

    return {
        "message": "Usuario inactivado correctamente"
    }