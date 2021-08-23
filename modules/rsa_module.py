from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from modules.constants import *
import base64

_FORMAT = Messaging.FORMAT


def gen_keys(bits: int = 1024) -> tuple:
    """
    Генерирует ключи.

    :param bits: количество бит ключа (нельзя зашифровать сообщение ключом, который короче соообщения)
    :return: кортеж из ключей (закрытый, открытый) в байтовом формате
    """

    # генерирует приватный ключ
    key = RSA.generate(bits)

    # переводим в битовый формат
    private_key = key.export_key()
    public_key = key.public_key().export_key()

    return private_key, public_key


def encrypt(public_key: bytes, msg: str) -> bytes:
    """
    Шифрует данное сообщение данным ключом.

    :param msg: сообщение
    :param public_key: открытый ключ
    :return: зашифрованное сообщение

    """

    # делаем из строки байты
    msg = msg.encode(_FORMAT)

    # превращаем байты в ключ-объект
    public_key = RSA.importKey(public_key)

    cipher = PKCS1_OAEP.new(public_key)  # шифр = алгоритм.???(публичный ключ)
    encrypted_message = cipher.encrypt(msg)  # зашифрованное сообщение = шифр.зашифровать(сообщение)

    # доп кодирование
    encrypted_message = base64.b64encode(encrypted_message)

    return encrypted_message


def decrypt(private_key: bytes, encr_enc_message: bytes) -> str:
    """
    Расшифровывает данное сообщение данным ключом.

    :param encr_enc_message: зашифрованное, закодированное сообщение
    :param private_key: закрытый ключ
    :return: расшифрованное сообщение

    """

    # декодируем сообщение
    encrypted_message = base64.b64decode(encr_enc_message)

    # импорт ключей
    private_key = RSA.importKey(private_key)

    cipher = PKCS1_OAEP.new(private_key)  # шифр = алгоритм.???(приватный ключ)
    decrypted_message = cipher.decrypt(encrypted_message)  # сообщение = шифр.расшифровать(зашифрованное сообщение)

    # делаем из полученной строки-байтов строку
    decrypted_message = decrypted_message.decode(_FORMAT)

    return decrypted_message


if __name__ == '__main__':
    priv_key, publ_key = gen_keys()
    __ENCRYPTED_MSG = '!e'

    msg = "Жопа..."  # сообщение, которое хотим отправить
    encrypted_msg = encrypt(publ_key, msg)
    encoded_msg = f'{__ENCRYPTED_MSG} '.encode(_FORMAT) + encrypted_msg

    inc_message = encoded_msg.decode(_FORMAT)
    # сервер получил:
    # {self.__ENCRYPTED_MSG} {encrypted_msg}
    # !e 8x329e8x7ndch2837ycd2h8b7hv32

    prefix, encrypted_encoded_message = inc_message.split(' ')
    decrypted = decrypt(priv_key, encrypted_encoded_message)
    print(f'Decrypted message: "{decrypted}"')
