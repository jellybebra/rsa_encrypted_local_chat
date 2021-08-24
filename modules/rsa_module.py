from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from modules.constants import *
import base64

_FORMAT = Messaging.FORMAT


def gen_keys(bits: int = 1024) -> tuple:
    """
    Генерирует ключи.

    :param bits: количество бит ключа (нельзя зашифровать сообщение ключом, который короче соообщения)
    :return: кортеж из ключей (закрытый, открытый) в байтовом формате для отправки через сокет
    """

    key = RSA.generate(bits)
    private_key: bytes = key.export_key()
    public_key: bytes = key.public_key().export_key()

    return private_key, public_key


def encrypt(public_key: bytes, message: str) -> bytes:
    """
    Шифрует сообщение данным ключом.

    :param message: сообщение
    :param public_key: открытый ключ
    :return: зашифрованное сообщение
    """

    public_key = RSA.importKey(public_key)  # bytes -> object
    cipher = PKCS1_OAEP.new(public_key)  # ничего не понятно

    message: bytes = message.encode(_FORMAT)  # str -> bytes
    encrypted_message: bytes = cipher.encrypt(message)  # зашифрованное сообщение = шифр.зашифровать(сообщение)
    encrypted_encoded_message: bytes = base64.b64encode(encrypted_message)  # для отправки через сокет

    return encrypted_encoded_message


def decrypt(private_key: bytes, encrypted_encoded_message: bytes) -> str:
    """
    Расшифровывает закодированное с помощью base64 зашифрованное данным ключом сообщение.

    :param encrypted_encoded_message: зашифрованное, закодированное сообщение
    :param private_key: закрытый ключ
    :return: расшифрованное сообщение
    """

    private_key = RSA.importKey(private_key)  # импорт ключей
    cipher = PKCS1_OAEP.new(private_key)  # ничего не понятно

    encrypted_message: bytes = base64.b64decode(encrypted_encoded_message)  # убираем base64
    decrypted_encoded_message: bytes = cipher.decrypt(encrypted_message)
    decrypted_message: str = decrypted_encoded_message.decode(_FORMAT)  # bytes -> str

    return decrypted_message
