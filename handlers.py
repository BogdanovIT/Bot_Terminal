from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
import kbds as kb 
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import database.requests as rq
import cv2, os
from config import TOKEN
import aspose.barcode as barcode
#from aspose.imaging.watermark import WatermarkRemover

bot = Bot(TOKEN)
router = Router()

class Search(StatesGroup):
    NS_code = State()
    Bar_Code = State()
    Bar_Code_reply = State()
    Show_image = State()
    Make_cell = State()
    Find_half = State()

class Admin(StatesGroup):
    load_update = State()


@router.message(F.file )

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.reg_user(message.from_user.id)
    await message.delete()
    await message.answer("Добро пожаловать!", reply_markup=kb.main_kb)
    
@router.message(F.text == "Поиск по NS")
async def search(message: Message, state: FSMContext):
    await state.set_state(Search.NS_code)
    await message.delete()
    await message.answer('Введите NS код товара, только цифры')

@router.message(F.text == "Нет ШК на товаре")
async def search(message: Message, state: FSMContext):
    await state.set_state(Search.Bar_Code_reply)
    await message.delete()
    await message.answer('Введите NS код товара, только цифры')

@router.message(Search.Bar_Code_reply)    
async def result(message: Message, state: FSMContext):
    if  len(message.text) != 7:
        await message.answer("Некорректный NS код. ", reply_markup=kb.main_kb)
        await state.clear()
    else:
        await message.delete()
        #await state.update_data(NS_code = str.upper(message.text))
        await state.update_data(NS_code = ("NS-")+(message.text))
        data = await state.get_data()
        await message.answer(f"Ищем ШК {data['NS_code']}")
        result = await rq.reply_barcode(data['NS_code'])
        name = await rq.get_name(data['NS_code'])
        if name == None or name == 0:
            await message.answer("Я ничего не нашёл. Проверьте NS", reply_markup=kb.main_kb)
            #await message.answer_photo(photo='https://ih1.redbubble.net/image.3243769575.1059/st,small,507x507-pad,600x600,f8f8f8.jpg')
            await state.clear()
        else:
            await message.answer(f"Нашёл: {name[0]}")
            await message.answer(f"Штрих код:\n{result[0]}", reply_markup=kb.main_kb)
            await state.clear()

@router.message(F.text == "Поиск по ШК")
async def search(message: Message, state: FSMContext):
    await state.set_state(Search.Bar_Code)
    await message.answer('Пришлите мне фото штрих кода и я попробую найти ваш товар')

@router.message(F.photo, Search.Bar_Code)
async def handle_photo(message: Message, state:FSMContext):
    await bot.download(
        message.photo[-1],
        destination=f"image_for_read.jpg")
    image_frame=cv2.imread("image_for_read.jpg")
    detector = cv2.barcode.BarcodeDetector()
    data = detector.detectAndDecode(image_frame)
    clear_data = data[0]
    await message.delete()
    ns_code = await rq.get_articul(clear_data)
    ns_code = ns_code[0]
    name = await rq.get_name(ns_code)
    result = await rq.get_product(ns_code)
    if name == None or name == 0:
            await message.answer("Что-то пошло не так. причин может быть несколько. \n Начни с начала", reply_markup=kb.main_kb)
            #await message.answer_photo(photo='https://ih1.redbubble.net/image.3243769575.1059/st,small,507x507-pad,600x600,f8f8f8.jpg')
            await state.clear()
    else:
        await message.answer(f"Нашёл: {name[0]}")
        for item in result:
            await message.answer(f"Ячейка: {item[1]}\nSSCC: {item[2]}\nКоличество: {item[3]} шт.", reply_markup=kb.main_kb)
            await state.clear()
    
@router.message(F.text == 'Дефрагментация')
async def defragmentation(message: Message):
    res = await rq.get_duplicate()
    for i in res:
        await message.answer(f"Можно слепить:{i[0]},  {i[1]}, {i[2]}, {i[3]}", reply_markup=kb.main_kb)
    
@router.message(Search.NS_code)    
async def result(message: Message, state: FSMContext):
    if  len(message.text) != 7:
        await message.answer("Некорректный NS код. ", reply_markup=kb.main_kb)
        await state.clear()
    else:
        await message.delete()
        #await state.update_data(NS_code = str.upper(message.text))
        await state.update_data(NS_code = ("NS-")+(message.text))
        data = await state.get_data()
        await message.answer(f"Ищем товар {data['NS_code']}")
        result = await rq.get_product(data['NS_code'])
        name = await rq.get_name(data['NS_code'])
        if name == None or name == 0:
            await message.answer("Я ничего не нашёл. Проверьте NS", reply_markup=kb.main_kb)
            #await message.answer_photo(photo='https://ih1.redbubble.net/image.3243769575.1059/st,small,507x507-pad,600x600,f8f8f8.jpg')
            await state.clear()
        else:
            await message.answer(f"Нашёл: {name[0]}", reply_markup=kb.main_kb)
            for item in result:
                await message.answer(f"Ячейка: {item[1]}\nSSCC: {item[2]}\nКоличество: {item[3]} шт.")
            await state.clear()

@router.message(F.text == 'Битые SSCC')
async def crash_sscc(message:Message):
    res = await rq.get_crashed()
    if res == 0 or res == None:
         await message.answer(f"Отличная работа, все SSCC в порядке")
    else:
        for item in res:
                await message.answer(f"Наименование: {item[0]}\nЯчейка: {item[1]}\nSSCC: {item[2]}\nКоличество: {item[3]}", reply_markup=kb.main_kb)

@router.message(F.text == "Как это выглядит?")
async def show_image(message: Message, state: FSMContext):
    await state.set_state(Search.Show_image)
    await message.delete()
    await message.answer('Введите NS код товара, только цифры')

@router.message(F.text == "Сделай штрих-код")
async def make_image(message: Message, state: FSMContext):
    await state.set_state(Search.Make_cell)
    await message.delete()
    await message.answer('Введите данные для генерации штрих кода')

@router.message(Search.Make_cell)
async def show_image(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(cell = message.text)
    data = await state.get_data()
    generator = barcode.generation.BarcodeGenerator(barcode.generation.EncodeTypes.CODE128)
    generator.code_text = data["cell"]
    generator.save("buffer_card.jpg")
    await message.answer_photo(FSInputFile(path="buffer_card.jpg"))
    await state.clear()

@router.message(Search.Show_image)
async def image_ready(message: Message, state: FSMContext):
    if  len(message.text) != 7:
        await message.answer("Некорректный NS код. ", reply_markup=kb.main_kb())
        await state.clear()
    else:
        await message.delete()
        await state.update_data(NS_code = ("NS-")+(message.text))
        data = await state.get_data()
        file_name = await rq.get_image(data['NS_code'])
        name = await rq.get_name(data['NS_code'])
        if name == None or name == 0:
            await message.answer("Я ничего не нашёл. Проверьте NS", reply_markup=kb.main_kb)
            await state.clear()
        else:
            await message.answer(f"Нашёл: {name[0]}", reply_markup=kb.main_kb)
            image_path = os.path.join(file_name)
            await message.answer_photo(FSInputFile(path=image_path))
            await state.clear()

@router.message(F.text== "Одиночки")
async def solo_block(message:Message):
     res = await rq.get_solo_blocks()
     for item in res:
          await message.answer(f"Наименование: {item[0]}\nЯчейка: {item[1]}\nSSCC: {item[2]}\nКоличество: {item[3]}", reply_markup=kb.main_kb)

@router.message(F.text == "Где моя половинка?")
async def search(message: Message, state: FSMContext):
    await state.set_state(Search.Find_half)
    await message.delete()
    await message.answer('Введите NS код товара, только цифры')
@router.message(Search.Find_half)
async def find_half(message: Message, state: FSMContext):
    if  len(message.text) != 7:
        await message.answer("Некорректный NS код. ", reply_markup=kb.main_kb)
        await state.clear()
    else:
        await message.delete()
        await state.update_data(NS_code = ("NS-")+(message.text))
        data = await state.get_data()
        half_name = await rq.get_half(data['NS_code'])
        solo = await rq.get_name(data['NS_code'])
        await message.answer(f"Ищем пару для {solo[0]}")
        result = await rq.get_product(half_name[0])
        name = await rq.get_name(half_name[0])
            
        if half_name[0] == "group":
            await message.answer("Функция работает только для бытовых сплит-систем. \nФункция сбора комплектов для канальных систем в разработке.", reply_markup=kb.main_kb)
            await state.clear()
        elif name == None or name == 0:
            await message.answer("Я ничего не нашёл. \nВозможно, это самостоятельная единица", reply_markup=kb.main_kb)
            #await message.answer_photo(photo='https://ih1.redbubble.net/image.3243769575.1059/st,small,507x507-pad,600x600,f8f8f8.jpg')
            await state.clear()
        else:
            await message.answer(f"Нашёл: {name[0]}", reply_markup=kb.main_kb)
            for item in result:
                await message.answer(f"Ячейка: {item[1]}\nSSCC: {item[2]}\nКоличество: {item[3]} шт.")
            await state.clear()

@router.message(F.text == "Есть идея!")
async def i_have_idea(message: Message):
    await message.delete()
    await message.answer("Если у вас есть предложения или замечания по работе бота, напишите мне: @Bogdanov_IT", reply_markup=kb.main_kb)