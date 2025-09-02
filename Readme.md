# Acerca de este proyecto
Se trata de una API de autenticación , basada en el estándar JWT, contiene:
* Endpoints para CRUD de Usuarios
* Recuperación de cuenta mediante validación de credenciales(email) y envío de código de verificación
* Roles de usuario
* Endpoints protegidos
* Validaciones con Pydantic y regex
* Y más
  
# INFO
  *Esta no es será la última versión de la api ya que planeo agregar test, más posibilidades, hacerla más resilente y comunicarla con otras y por supuesto mejorar la organización , arquitectura etc.*

# Instrucciones para ejecutar el proyecto

* Crear un entorno virtual para aislar dependencias:
    * `python -m venv mi_entorno`
   
    * Luego activarlo con:
      * `mi_entorno/Scripts/activate`
  
  
* Ejecutar el siguiente comando para instalar dependencias:
    * `pip install -r requirements.txt`

* Una vez instaladas las dependencias , posicionarse en la carpeta contenedora de el archivo **main.py**, en este caso la carpeta *users*

* Es necesario crear un archivo .env para establecer las variables de entorno, para eso mirar el archivo *.env.example* para tener una idea de como hacerlo

* Una vez hecho esto , ejecutar el siguiente comando para correr el servidor en el servidor local:
    * `fastapi dev main.py`

* Para leer la documentación de la API y saber como consumirla entrar en:
    * (http://127.0.0.1:8000/docs)
  
  
