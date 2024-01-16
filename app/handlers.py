from aiogram import Router, Bot
from aiogram.filters import CommandStart, Filter, Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from openai import OpenAI
import httpx

from app.database.requests import set_user, get_users

router = Router()

ADMINS = ['id', 'id']

client = OpenAI(
    api_key='ключ опенаи',
    http_client=httpx.Client(
        proxies="прокся",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)


def generate_answer(user_message):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{user_message}",
            }
        ],
        model="gpt-4",
    )
    return chat_completion.choices[0].message.content


class AdminProtect(Filter):
    def __init__(self):
        self.admins = ADMINS
    
    async def __call__(self, message: Message):
        return message.from_user.id in self.admins


class AntiFlood(StatesGroup):
    generating_message = State()


class Newsletter(StatesGroup):
    message = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.answer(text='Привет!')


@router.message(AdminProtect(), Command('newsletter'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Отправьте сообщение для рассылки!')


@router.message(AdminProtect(), Newsletter.message)
async def get_admin(message: Message, state: FSMContext, bot: Bot):
    users = await get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user.tg_id, text=message.text)
        except:
            print('user banned')
    await message.answer('Рассылка завершена!')


@router.message(AntiFlood.generating_message)
async def anti_flood(message: Message, state: FSMContext):
    await message.answer('Вы ещё не получили ответа! Если это ошибка, перезапустите бота /start.')


@router.message()
async def gpt_answer(message: Message, state: FSMContext):
    await state.set_state(AntiFlood.generating_message)
    answer = generate_answer(message.text)
    await message.answer(f'{answer}')
    await state.clear()
