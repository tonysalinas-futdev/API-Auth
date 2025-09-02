from pydantic import Field
import re
from fastapi import HTTPException
#Definimos fuciones para validar cada campo que lo necesite y así no repetimos código, el atributo required es para cuando no necesitemos que el camppo sea obligatorio



def password_validator(required=True):
    return Field(
        ... if required else None ,
        min_length=8,
        
        description="La contraseña debe tener una longitud minima de 8 caractéres y ademas incluir un símbolo especial entre @#$%&*+, una mayúscula y una minúscula ",
        

            )

def pattern_password_validation(valor):
    if not re.fullmatch(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%&*+])[a-zA-Z0-9@#$%&*+]{8,}$", valor):
        raise HTTPException(status_code=409, detail="La contraseña debe tener una longitud minima de 8 caractéres y ademas incluir un símbolo especial entre @#$%&*+")
    return valor


def phone_validator(required=True):
    return Field(... if required else None,
            pattern=r"^\+[0-9]{1,3}\s[0-9]{8,12}$",
            description="El número de teléfono debe cumplir con el formato de los ejemplos",
            examples=["+34 900457678", "+53 52124576", "+54 756123845"]
        
    )

def firstname_validator(required=True):
    return Field(
        ... if required else None,
        max_length=40,
        min_length=2,
        description="Primer Nombre , nada de caracteres especiales , números o espacios antes o después del nombre",
        

)


def lastname_validator(required=True):
    return Field(
        ... if required else None,
        max_length=40,
        min_length=2,
        description="Primer Nombre , nada de caracteres especiales , números o espacios antes o después del apellido",

)


def first_and_lastname_pattern(value):
    if not re.fullmatch(r"^(?!\s)[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{2,40}(?<!\s)$", value):
        raise HTTPException(status_code=409, detail="Este campo no soporta espacios antes o después de la cadena, ni cualquier caracter especial")
    return value

