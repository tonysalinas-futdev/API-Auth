from pydantic import Field,BaseModel,EmailStr, model_validator, field_validator
from validators import lastname_validator, firstname_validator, phone_validator, password_validator,first_and_lastname_pattern, pattern_password_validation
from typing import Optional


class UserBase(BaseModel):
    id:int
    first_name:str
    last_name:str
    email:EmailStr
    phone_number:str
    country:str
    address:str
    role:str
        
    class Config:
        from_attributes=True


class UserSend(BaseModel):
    first_name:str
    last_name:str
    email:EmailStr
    phone_number:str
    country:str
    address:str
    class Config:
        from_attributes=True
        


class UserCreate(BaseModel):
    first_name:str=firstname_validator()

    last_name:str=lastname_validator()

    @field_validator("first_name","last_name")
    def validate_name(cls, value):
        return first_and_lastname_pattern(value)
    
    
    password: str=password_validator()
    @field_validator("password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)
    
    email:EmailStr=Field(...)
    
    phone_number:str=phone_validator()

    country:str
    address: str


#Clase para inciar sesión
class UserSignIn(BaseModel):
    email:EmailStr=Field(...)
    
    password: str=password_validator()
    @field_validator("password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)
    


#Clae para actualizar Perfil
class UserUpdate(BaseModel):
    first_name:Optional[str]=firstname_validator(required=False)



    last_name:Optional[str]=lastname_validator(required=False)

    
    @field_validator("first_name","last_name")
    def validate_name(cls, value):
        return first_and_lastname_pattern(value)
    
    email:Optional[EmailStr]=None
    phone_number:Optional[str]=phone_validator(required=False)

    

    country:Optional[str]=None
    address: Optional[str]=None


class UpdatePassword(BaseModel):
    password: str=password_validator()

    
    new_password:str=password_validator()
    
    @field_validator("new_password","password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)
    
    @model_validator(mode="after")
    def password_validation(cls, values):
        if values.password==values.new_password:
            raise ValueError("La nueva contraseña debe ser diferente de la vieja")
        return values
    




class TokenRefreshResponse(BaseModel):
    access_token:str
    token_type:str
    user: UserBase


class TokenResponse(TokenRefreshResponse):
    refresh_token:str



class EmailRequest(BaseModel):
    email: EmailStr

class CodeRequest(BaseModel):
    code:int
    

class PasswordRequest(BaseModel):
    password:str=password_validator()
    @field_validator("password")
    def validate_password(cls, valor):
        return pattern_password_validation(valor)
    