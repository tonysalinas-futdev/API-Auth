from models import Role
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

#Función para crear los roles en la base de datos si no existen ya
async def init_role(session:AsyncSession):
    stmt=select(Role).where(Role.name.in_(["admin","member"]))
    result=await session.execute(stmt)
    existing=result.scalars().all()
    roles=[rol.name for rol in existing]

    if "admin" not in roles:
        admin_role=Role(name="admin")
        session.add(admin_role)
        await session.commit()
    if "member" not in roles:
        admin_role=Role(name="member")
        session.add(admin_role)
        await session.commit()