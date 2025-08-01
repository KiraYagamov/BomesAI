from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import telebot
from User import User

# Загрузка модели (первый запуск скачает ~1.5 ГБ)
# model_name = "ai-forever/rugpt3large_based_on_gpt2"
# model_name = "ai-forever/ruGPT-3.5-13B"
model_name = "sberbank-ai/rugpt3large_based_on_gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Создаём пайплайн для генерации текста
chatbot = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device="cuda",  # Используем GPU если есть
)

# Параметры генерации
generation_config = {
    "do_sample": True,
    "temperature": 0.22,
    "top_k": 60,
    "top_p": 0.9,
    "max_new_tokens": 30,
    "no_repeat_ngram_size": 2
}

input_bot_data = "Идет диалог между пользователем и умным и вежливым чат-ботом:"

def generate_answer(prompt, dialog, recursion_count=0):
    global input_bot_data
    if recursion_count > 3:
        return "Бот не знает, что ответить"
    full_prompt = f"{input_bot_data}{"\n"}{"\n".join(dialog)}\n{prompt}"
    result = chatbot(full_prompt, **generation_config)
    bot_response = result[0]['generated_text'].split("А чат-бот ему ответил - ")[-1].strip().split("\n")[0]
    if bot_response.count("?") > 1:
        return generate_answer(prompt, dialog, recursion_count + 1)
    print(f"{full_prompt}{bot_response}")
    return bot_response

token = "7477847721:AAHim6MHOnH6JI6jbE7T5Nvuud6bVAZHZd0"
bot = telebot.TeleBot(token)

users = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Вас приветствует искусственный интеллект BomesAI!\nВведите любое сообщение, чтобы начать общаться")
    user = User(message.chat.id)
    users[message.chat.id] = user

@bot.message_handler(commands=['reset'])
def reset_message(message):
    bot.send_message(message.chat.id, "История ваших сообщений сброшена")
    user = users[message.chat.id]
    user.dialog.clear()

@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.chat.id not in users.keys():
        bot.send_message(message.chat.id, "Для начала введите /start")
        return
    user = users[message.chat.id]
    user_input = message.text
    prompt = f"Пользователь сказал - \"{user_input}\"\nА чат-бот ему ответил - "
    msg = bot.send_message(message.chat.id, "Бот думает...")
    bot_response = generate_answer(prompt, user.dialog)
    bot.edit_message_text(bot_response.replace("\"", ""), message.chat.id, msg.id)
    user.dialog.append(f"{prompt}{bot_response}")
    if len(user.dialog) > 10:
        user.dialog.pop(0)
    print("----------------------------")

bot.infinity_polling()
