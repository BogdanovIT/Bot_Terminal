from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///inventory_copy.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Barcode(Base):
    __tablename__ = 'barcodes'
    product: Mapped[str] = mapped_column()
    barcode: Mapped[str] = mapped_column(primary_key=True)
    articul: Mapped[str] = mapped_column()

class Item(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    product: Mapped[str] = mapped_column()
    cell: Mapped[str] = mapped_column()
    sscc: Mapped[str] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    available_quantity: Mapped[int] = mapped_column()
    reserve: Mapped[int] = mapped_column()
    primary_code: Mapped[str]= mapped_column()

class Catalog(Base):
    __tablename__ = 'catalog'
    id: Mapped[int] = mapped_column(primary_key=True)
    product: Mapped[str] = mapped_column()
    primary_code: Mapped[str] = mapped_column()
    second_key: Mapped[str] = mapped_column()

class Image_Base(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column()
    primary_code: Mapped[str] = mapped_column()

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)