from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI
import httpx

router = Router()

client = OpenAI(
    api_key='код от openai',
    http_client=httpx.Client(
        proxies="адрес прокси",
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
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text='Привет!')


@router.message()
async def gpt_answer(message: Message):
    answer = generate_answer(message.text)
    await message.answer(f'{answer}')
