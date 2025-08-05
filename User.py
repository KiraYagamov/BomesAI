class User:
    def __init__(self, chatID):
        self.chatID = chatID
        self.history = [{
            "role": "assistant",
            "content": "Меня зовут BomesAI и я твой личный помощник! Меня создал Егор Столбов на основе модели DeepSeek. Пожалуйста, имейте ввиду, что я помню только последние 10 сообщений."
        }]
        self.waiting = False