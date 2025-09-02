from fastapi import Depends, APIRouter, HTTPException, status, Body, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import database, schemas, sqlalchemyrepo
from jwt_utils import  get_current_user, generate_token,refresh_token, verify_refresh
from send_sms import send_email


#Dependencia para obtener la session de la base de datos
async def get_db(db:AsyncSession=Depends(database.get_session)):
    return db


#Dependencia para obtener el repo de sqlalchemy con la sesion
def get_repo(session:AsyncSession=Depends(get_db)):
    return sqlalchemyrepo.UserSQLAlchemyRepository(session)


#Dependencia para obtener el repositorio para realizar las operaciones con el token
def get_token_repo(session:AsyncSession=Depends(get_db)):
    return sqlalchemyrepo.TokenSQLAlchemyRepository(session)


#Dependencia para crear un access y un refresh token con los datos del usuario apropiado
async def get_token(user, role):
    #Creamos el access token con los datos del usuario
    token=generate_token(user.first_name, role , user.email, user.id)
    #Creamos el refresh
    token_refresh=refresh_token(user.id)
    #Devolvemos ambos y ademos todos los datos del usuario para que el frontend los use
    return {"access_token":token, "token_type":"bearer","refresh_token": token_refresh, "user":{
            "id":user.id,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email":user.email,
            "country":user.country,
            "address":user.address,
            "phone_number":user.phone_number,
            "role":role
}}

#Definimos el router con el prefijo 
router=APIRouter(prefix="/users", tags=["Users"])



#Ruta para hacer login, verificar credenciales y devolver el token
@router.post("/login", status_code=status.HTTP_200_OK, summary="Ruta para iniciar sesion", response_model=schemas.TokenResponse)
async def login(model:schemas.UserSignIn, response:Response, service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo) ):
    #Comprobamos las credenciales del usuario con la función creada para eso
    user=await service.sign_in(model)
    rol=user.role.name
    #Generamos el access_token y el refresh_token y lo devolvemos como cookies
    data=await get_token(user,rol)
    
    response.set_cookie(
        key="access_token",
        value=data.get("access_token"),
        httponly=True,
        secure=True,
        max_age=60*60*48,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=data.get("refresh_token"),
        httponly=True,
        secure=True,
        max_age=60*60*48,
        samesite="lax"
    )
    return data



#Ruta para crear una cuenta, guarda los datos y loguear automaticamente
@router.post("/sign_up", status_code=status.HTTP_201_CREATED, summary="Ruta para crear una cuenta", response_model=schemas.TokenResponse)
async def sign_up(model:schemas.UserCreate, service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo)):
    user=await service.create_account(model)
    rol=user.role.name
    return await get_token(user,rol)


#Ruta para actualizar perfil
@router.put("/update",status_code=status.HTTP_202_ACCEPTED, summary="Ruta para actualizar la info", response_model=schemas.UserSend)
async def update(model:schemas.UserUpdate, service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo),data=Depends(get_current_user)):
    user_id=data.get("id")
    user=await service.update_account(model, user_id)
    return user



#Ruta para obtener los datos de tu perfil
@router.get("/get_profile", status_code=status.HTTP_200_OK, response_model=schemas.UserSend, summary="Ruta para que el cliente obtenga los datos de su perfil")
async def get_profile(service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo),data=Depends(get_current_user)):
    usuario=await service.get_by_id(data.get("id"))
    return usuario


#Ruta para cambiar la contraseña
@router.patch("/change_password", summary="Ruta para cambiar de contraseña", status_code=status.HTTP_202_ACCEPTED)
async def change_password(model:schemas.UpdatePassword,service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo), data=Depends(get_current_user)):
    resultado=await service.change_password(data.get("id"), model)
    return resultado


#Ruta para eliminar datos
@router.delete("/delete",status_code=status.HTTP_202_ACCEPTED) 
async def delete(service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo),data=Depends(get_current_user)):
    await service.delete_account(data.get("id"))
    return JSONResponse(content="Cuenta elminada correctamente")


#Ruta para acceder obtener un nuevo access_token a partirt del refresh_token
@router.post("/refresh_token", status_code=status.HTTP_200_OK, response_model=schemas.TokenRefreshResponse)
async def refresh(token:str= Body(...), service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo)):
    #Verificamos el token 
    user_id=verify_refresh(token)
    #Obtenemos los datos del usuario cuyo id venia en el token
    user=await service.get_by_id(user_id)
    rol=user.role.name
    #Generamos un nuevo token de acceso usando la funcion get_token
    new_token=await get_token(user,rol)
    #Eliminamos el token refresh de los datos para asi no tener que repetir código
    new_token.pop("refresh_token")
    return new_token


@router.post("/forgot_password", status_code=status.HTTP_200_OK,summary="El cliente debe enviar su email a este endopint si olvidó su contraseña")
async def restore_password(request:schemas.EmailRequest, service:sqlalchemyrepo.TokenSQLAlchemyRepository=Depends(get_token_repo), service_user:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo)):
    user=await service_user.get_by_email(request.email)
    if user:
        token=await service.save_token(user.id)
        text=f"Aqui tiene su token para cambiar de contraseña: {token.codigo}"
        try:
            send_email("Cambio de contraseña", request.email, "EcomercceTony", text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    return JSONResponse(content="Hemos enviado un email a ese correo")


#Endpoint para recibir el código de verificación y hacer validaciones
@router.post("/receive_code", status_code=status.HTTP_200_OK,summary="Endpoint para verificar el código enviado al cliente y devolver el id de ese usuario")
async def verify_code(request:schemas.CodeRequest, service:sqlalchemyrepo.TokenSQLAlchemyRepository=Depends(get_token_repo), user_service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo)):
    flag=await service.verify_token(request.code)
    if flag:
        token=await service.get_token(request.code)
        user=await user_service.get_by_id(token.user_id)
        return {"message":"Código verificado exitosamente", "user_id":user.id}



#Endpoint para cambiar la contraseña del usuario cuyo id está asociado al token de verificación
@router.post("/save_new_password/{user_id}", status_code=status.HTTP_200_OK, summary="Endpoint que recibe el id del usuario y la nueva contraseña, la cambia y la guarda en la base de datos")
async def save_password(user_id:int,request:schemas.PasswordRequest, user_service:sqlalchemyrepo.UserSQLAlchemyRepository=Depends(get_repo)):
    find_user=await user_service.get_by_id(user_id)
    if find_user:
        await user_service.forgot_password(request.password,find_user.email)
    return JSONResponse(content="Contraseña modificada exitosamente", status_code=200)

