import asyncio
from fastapi import  Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from main import app

#Middleware para timeout
@app.middleware("http")
async def timeout(request:Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=20)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="El tiempo de espera se ha agotado")
    




origins=[
    "http://localhost:4200",
    "http://127.0.0.1:4200" ,
    "http://localhost:5000"
        
        ]

app.add_middleware(
    CORSMiddleware,
    #Origenes que permitimos
    allow_origins=origins,
    
    allow_credentials=True,
    #Todos los emtodos http
    allow_methods=["*"],
    #Todos los encabezados
    allow_headers=["*"] 

)


