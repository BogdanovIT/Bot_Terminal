from database.models import async_session
from database.models import Item, User, Barcode, Image_Base, Catalog
from sqlalchemy import distinct, not_, select, func
from sqlalchemy.orm import selectinload, subqueryload
from sqlalchemy.sql.functions import count

async def reg_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()
    
async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))

async def get_image(clear_data):
    async with async_session() as session:
        return await session.scalar(select(Image_Base.file_name).where(Image_Base.primary_code == clear_data))

async def get_product(clear_data):
    async with async_session() as session:
        items = await session.execute(select(Item.product, Item.cell, Item.sscc, Item.quantity).where(Item.primary_code == clear_data))
        result = items.fetchall()
        return result

async def get_name(clear_data):
    async with async_session() as session:
        name = await session.execute(select(Item.product).where(Item.primary_code == clear_data))
        result = name.fetchone()
        return result

async def reply_barcode(clear_data):
     async with async_session() as session:
        try:      
            barcode = await session.execute(select(Barcode.barcode).where(Barcode.articul == clear_data))
            result = barcode.fetchone() 
        except:
            pass                    
        return result

async def get_articul(clear_data):
    async with async_session() as session:
        try:      
            articul = await session.execute(select(Barcode.articul).where(Barcode.barcode == clear_data))
            result = articul.fetchone() 
        except:
            pass                    
        return result

async def get_crashed():
    async with async_session() as session:
        crashed_sscc = await session.execute(
    select(Item.product, Item.cell, Item.sscc, Item.quantity)
    .where(func.length(Item.sscc) != 11)
    .where(~Item.sscc.like("S4005%"))
    .where(~Item.sscc.like("4005%"))
    .where(~Item.sscc.like("product%"))
    .where(~Item.sscc.like("cell%"))
    .where(~Item.sscc.like("sscc%"))
    .where(~Item.sscc.like("Товар%"))
    .where(~Item.sscc.like("Ячейка%"))
    .where(~Item.sscc.like("Номер SSCC%"))
    .where(~Item.cell.like("NVM%"))
    .where(~Item.product.like("%паллет%"))
    )
        result = crashed_sscc.fetchall()
        return result
  
async def get_solo_blocks():
    async with async_session() as session:
        solo_blocks = await session.execute(
    select(Item.product, Item.cell, Item.sscc, Item.quantity)
    .where(Item.primary_code.in_(select(Item.primary_code).group_by(Item.primary_code).having(count() == 1)))
    .where(Item.quantity == 1)
    .where(~Item.cell.like("%KARANTIN"))
    .where(~Item.cell.like("%$%"))
    .where(~Item.cell.like("%OUT%"))
    .where(~Item.cell.like("&BRAK"))
    .where(Item.product.like("%блок%"))
    )
        result = solo_blocks.fetchall()
        return result
    
async def get_duplicate():
    async with async_session() as session:
        items = await session.execute(
    select(Item.product, Item.cell, Item.sscc, Item.quantity)
    .where(~Item.cell.like("%$%"))
    .where(~Item.cell.like("%KARANTIN"))
    .where(~Item.cell.like("%OUT%"))
    .where(~Item.cell.like("&BRAK"))
    .where(Item.primary_code.in_(
        select(Item.primary_code)
        .group_by(Item.primary_code)
        .having(count(Item.cell.distinct()) >= 2)
        .where(~Item.cell.like("%$%"))
        .where(~Item.cell.like("%KARANTIN"))
        .where(~Item.cell.like("&BRAK"))
        .where(~Item.cell.like("%OUT%"))
    )))
        result = items.fetchall()
        return result

async def get_half(clear_data):
    async with async_session() as session:
        try:
            half_articul = await session.execute(select(Catalog.second_key).where(Catalog.primary_code == clear_data))
            result = half_articul.fetchone()
        except:
            pass
        return result

async def party_hard():
    async with async_session() as session:
        # здесь будет запрос на расстановку товара, находящегося в ячейках IN по существующим ячейкам при наличии такого товара на остатках склада
        ...