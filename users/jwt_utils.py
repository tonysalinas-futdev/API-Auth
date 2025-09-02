from jose import jwt, JWTError
from datetime import datetime, timedelta 
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
import os
from dotenv import load_dotenv

#Cargamos las variables de entorno
load_dotenv()

#Instanciamos la clase necesaria para extraer los tokens de autorizacion de las cabeceras de las peticiones a las rutas protegidas e indicamos la ruta en la que se debe obtener el token de autenticación
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

#Función para generar el token
def generate_token(nombre: str, role: str , email:str, user_id: int ):

    #Establecemos la fecha de expiración(15 minutos a partir de su creación)
    expire=datetime.now()+timedelta(minutes=15)
    #Creamos el paylodad con los datos que llevará el token
    payload={
        "sub": nombre,
        "role": role,
        "exp":int(expire.timestamp()),
        "id": user_id,
        "email": email,
        "type":"access_token"
    }

    #Lo codificamos accediendo a las variables con la clave secreta y el algoritmo de encriptaciobn
    token=jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

    return token

#Función para decodificar el token y obtener los datos del usuario autenticado
def get_current_user(token:str=Depends(oauth2_scheme)):

    
    try:
        #Intentamos decodificarlo
        decoded=jwt.decode(token ,os.getenv("SECRET_KEY") , algorithms=[os.getenv("ALGORITHM")])

        #Si lo logramos, comprobamos que el token sea de acceso
        if decoded.get("type")=="access_token":
            #Si lo es , retornamos los datos del payload
            return {
        "name":decoded.get("sub"),
        "role":decoded.get("role"),
        "id":decoded.get("id"),
        "email":decoded.get("email")
    }
        
    
    #Si ocurre un error lanzamos una excepción 
    except JWTError:
        raise  HTTPException(
        status_code=401,
        detail="Token inválido o modificado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    

#Función para generar un refresh_token para así poder prolongar la autenticación
def refresh_token(user_id):
    #Definimos el tiempo de expiracion en segundos 
    exp=int((datetime.utcnow()+timedelta(days=7)).timestamp())
    #Definimos el payload con los datos del usuario
    payload={
        "user_id": user_id,
        "exp": exp,
        "type" : "refresh_token"
    }

    #Lo codificamos
    refresh=jwt.encode(payload,os.getenv("SECRET_KEY"),os.getenv("ALGORITHM"))
    return refresh 

#Función para verificar el refresh token
def verify_refresh(token):
    try:
        #Lo decodificamos
        decode=jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    except JWTError:
        raise  HTTPException(
        status_code=401,
        detail="Token inválido o modificado",
        
    )
    #Comprobamos que la fecha de expiracion sea anterior a la de hoy y que el tipo del token sea "refresh"
    today=datetime.utcnow().timestamp()
    if decode.get("type")=="refresh_token" and decode.get("exp")>today:
        return decode.get("user_id")
