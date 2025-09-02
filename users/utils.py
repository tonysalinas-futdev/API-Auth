from passlib.hash import bcrypt

#Funcion para hashear password
def hash_password(password):
    hashed=bcrypt.hash(password)
    return hashed
#Función para verificarla
def verify_password(password,hashed_password):
    return bcrypt.verify(password, hashed_password)
        

