from repository import AbstractClientUser,AbstractToken
import schemas
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import User, OTP,Role
from fastapi import HTTPException
from utils import hash_password, verify_password
import random, datetime
import re


class UserSQLAlchemyRepository(AbstractClientUser):

    #Función para obtener un usuario de la base de datos por su id
    async def get_by_id(self, user_id:int):

        stmt=select(User).options(selectinload(User.role)).where(User.id==user_id)
        result= await self.session.execute(stmt)
        user=result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    #Funcion para obtener un usuario de la base de datos por su email
    async def get_by_email(self, email):
        stmt=select(User).options(selectinload(User.role)).where(User.email==email)
        result=await self.session.execute(stmt)
        user=result.scalar_one_or_none()
        

        
        return user
            

    #Funcion para loguearse
    async def sign_in(self, model:schemas.UserSignIn):
        data=model.model_dump()
        user=await self.get_by_email(data["email"])

        if user:
            if verify_password(data["password"], user.password):
                
                return user
                    
                
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        else:
            raise HTTPException(status_code=404, detail="Ese email no existe")

        

    #Funcion para crearse una cuenta
    async def create_account(self, model:schemas.UserCreate):

        data=model.model_dump()
        existing=await self.get_by_email(data["email"]) 
        if existing:
            raise HTTPException(status_code=409, detail="Ese email ya existe")
        hash_pass=hash_password(data["password"])
        data["password"]=hash_pass
        stmt=select(Role).where(Role.name=="member")
        result=await self.session.execute(stmt)
        rol=result.scalar_one_or_none()
        if not rol:
            raise HTTPException(status_code=404, detail="El rol memeber no existe en la base de datos")
        new_user=User(**data, role_id=rol.id)
        
            
        try:
            self.session.add(new_user)  
            await self.session.commit()      
            await self.session.refresh(new_user)
            stmt = select(User).options(selectinload(User.role)).where(User.id == new_user.id)
            result = await self.session.execute(stmt)
            user_with_role = result.scalar_one()
            return user_with_role
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Ha fallado la creacion de la cuenta")



    #Funcion para actualizar la cuenta
    async def update_account(self, model: schemas.UserUpdate, user_id:int):
        user=await self.get_by_id(user_id)
        data=model.model_dump(exclude_none=True)
        try:
            for key, value in data.items():
                setattr(user,key,value)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Error : {str(e)}")
        
        

        

    async def delete_account(self, user_id:int):
        user=await self.get_by_id(user_id)
        if user:
            try:
                await self.session.delete(user)
                await self.session.commit()
                return True
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=500 , detail=f"Error : {str(e)}") 
            
    #Funcion para cambiar la contraseña
    async def change_password(self,user_id:int, model:schemas.UpdatePassword):
        user=await self.get_by_id(user_id)
        data=model.model_dump()
        if user:
            if verify_password(data["password"], user.password):
                try:
                    user.password=hash_password(data["new_password"])
                    await self.session.commit()
                    return {"message": "Contraseña actualizada exitosamente"}
                except Exception as e:
                
                    await self.session.rollback()
                    raise HTTPException(status_code=500, detail=f"No se pudo cambiar la contraseña error: {e}")
            else:
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")
            

    #Funcion para cambiar la contraseña solo si la olvidaste
    async def forgot_password(self, new_password, email:str):
            hash_passw=hash_password(new_password)
            user=await self.get_by_email(email)
            user.password=hash_passw
            try:
                await self.session.commit()
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
                
        

        
    

class TokenSQLAlchemyRepository(AbstractToken):
    #Funcion para guardar un token enviado en la base de datos
    async def save_token(self,user__id:int):
        expi=(datetime.datetime.utcnow()+datetime.timedelta(minutes=5))
        code=random.randint(100000, 999999)
        token=OTP(exp=expi,codigo=code, user_id=user__id)
        try:
            self.session.add(token)
            await self.session.commit()
            await self.session.refresh(token)
            return token
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=404, detail=f"No se pudo guardar el token: {e}")
        
    #Funcion para obtener un token en la base de datos
    async def get_token(self,code:int):
        stmt=select(OTP).where(OTP.codigo==code)
        result=await self.session.execute(stmt)
        token=result.scalar_one_or_none()
        if not token:
            raise HTTPException(status_code=404, detail="Codigo invalido")
        return token
    
    #Funcion para verificar un token
    async def verify_token(self,code:int ):
        token=await self.get_token(code)
    
        if datetime.datetime.utcnow()>token.exp:
            raise HTTPException(status_code=404, detail="Codigo vencido")
        
        if token.used==True:
            raise HTTPException(status_code=404, detail="Codigo usado")

        token.used=True
        await self.session.commit()

        return True
        
        
