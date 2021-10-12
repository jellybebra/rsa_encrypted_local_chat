import os
os.system("")  # включает цвета в CMD


class Messaging:
    WIDE_MSG = '!w'  # широковещательное сообщение
    ENCRYPTED_MSG = '!e'  # зашифрованное сообщение
    KEY_REQUEST_MSG = '!kr'  # запрос ключа
    KEY_ANSWER_MSG = '!ka'  # ответ на запрос ключа
    ACTIVE_CLIENTS_MSG = '!ac'
    PORT = 8080
    BPM = 512  # Bits Per Message (для кодир-я 1 сообщения) (взяли максимальное из-за лени)  # TODO: понизить
    FORMAT = 'utf-8'  # кодировка


class Style:
    WHITE = '\033[0m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    RED1 = '\033[31m'
    RED2 = '\033[91m'
