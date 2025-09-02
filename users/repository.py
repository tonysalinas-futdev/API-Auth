from abc import ABC, abstractmethod
import schemas
from sqlalchemy.ext.asyncio import AsyncSession



class AbstractClientUser(ABC):
    def __init__(self, session:AsyncSession):
        self.session=session
        

    @abstractmethod
    async def update_account(self, model,user_id:int):
        pass

    @abstractmethod
    async def delete_account(self,user_id:int):
        pass

    @abstractmethod
    async def create_account(self,model:schemas.UserCreate):
        pass
    
    @abstractmethod
    async def sign_in(self, model:schemas.UserSignIn):
        pass

    @abstractmethod
    async def change_password(self, new_password,user_id,password):
        pass


class AbstractToken(ABC):
    def __init__(self, session:AsyncSession):
        self.session=session
        
        
    @abstractmethod
    async def save_token(token):
        pass

    @abstractmethod
    async def get_token(token_id):
        pass

    @abstractmethod
    async def verify_token(token):
        pass