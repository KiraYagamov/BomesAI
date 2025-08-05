# Выбор базового образа с Python
FROM python:3.12-alpine
# Установка рабочей директории
WORKDIR /app
# Копирование файлов проекта
COPY . /app
# Установка зависимостей
RUN pip install openai
RUN pip install aiogram
# Запуск приложения
CMD ["python", "main.py"]