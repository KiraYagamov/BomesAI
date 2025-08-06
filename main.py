from aiogram import Bot, Dispatcher
from openai import AsyncOpenAI
from config import *
import asyncio
from User import User

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

current_token_index = 0
current_model_index = 0

client = None

users = {}

async def create_client():
    global client, current_token_index
    if client != None:
        await client.close()
        print("Client closed")
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_TOKENS[current_token_index],
    )
    print(f"New token: {API_TOKENS[current_token_index]}")
    current_token_index += 1
    if current_token_index >= len(API_TOKENS):
        current_token_index = 0
        current_model_index += 1
        if current_model_index >= len(MODELS):
            current_model_index = 0

@dp.message()
async def any_message(message):
    global current_model_index
    if message.chat.id not in users.keys():
        await message.answer("Привет! Меня зовут BomesAI и я твой личный помощник! Пожалуйста, имейте ввиду, что я помню только последние 10 сообщений.")
        users[message.chat.id] = User(message.chat.id)
        return
    user = users[message.chat.id]
    if user.waiting:
        await message.answer("Пожалуйста, подождите. Ваш запрос еще обрабатывается!")
        return
    user.waiting = True
    think = await message.answer("Бот думает...")
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        user.history.append({
            "role": "user",
            "content": message.text
        })
        completion = await client.chat.completions.create(
            extra_body={},
            model=MODELS[current_model_index],
            messages=user.history
        )
        ai_answer = completion.choices[0].message.content
        user.history.append({
            "role": "assistant",
            "content": ai_answer
        })
        user.history = [user.history[0]] + user.history[-10:]
        user.waiting = False
        await bot.delete_message(message.chat.id, think.message_id)
        await message.answer(ai_answer, parse_mode="Markdown")
    except:
        await bot.delete_message(message.chat.id, think.message_id)
        user.waiting = False
        await create_client()
        await any_message(message)

async def main():
    await create_client()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())