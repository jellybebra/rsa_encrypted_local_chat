import os
os.system("")  # включает цвета в CMD

# TODO: Попробовать понизить BPM для ускорения


class Messaging:
    WIDE_MSG = '!w'  # широковещательное сообщение
    ENCRYPTED_MSG = '!e'  # зашифрованное сообщение
    KEY_REQUEST_MSG = '!kr'  # запрос ключа
    KEY_ANSWER_MSG = '!ka'  # ответ на запрос ключа
    ACTIVE_CLIENTS_MSG = '!ac'
    PORT = 8080
    BPM = 512  # Bits Per Message - число бит для кодир-я 1 сообщения (взяли максимальное из-за лени)
    FORMAT = 'utf-8'  # кодировка


# Class of different styles
class Style:
    BOLD = '\033[1m'  # не особо видна разница, ярче чем WHITE
    UNDERLINE = '\033[4m'

    WHITE = '\033[0m'
    GREY = '\033[37m'  # не работает в CMD
    BLACK = '\033[30m'  # нахуя нужен не понятно

    RED1 = '\033[31m'
    RED2 = '\033[91m'  # розовый

    GREEN1 = '\033[32m'
    GREEN2 = '\033[92m'  # чуть ярче

    BLUE1 = '\033[34m'  # синий
    BLUE2 = '\033[94m'  # голубой

    PINK = '\033[95m'  # фиолетовый
    YELLOW = '\033[93m'  # цвет мочи
    MAGENTA = '\033[35m'  # фиолетовый

    CYAN1 = '\033[36m'  # бирюзовый
    CYAN2 = '\033[96m'  # бирюзовый


if __name__ == '__main__':
    print(Style.CYAN2 + "Hello, World!" + Style.WHITE)
