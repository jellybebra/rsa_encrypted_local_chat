import rsa


def gen_keys(bits=1024):
    """

    :param bits: количество бит ключа
    :return: возвращает кортеж (открытый ключ, закрытый ключ)

    Есть определенная закономерность, которая требует,
    чтобы длина ключа была больше длины самого сообщения,
    при том в значительное количество раз.

    """

    return rsa.newkeys(bits)  # генерируем ключи


def encrypt(public_key, message):
    """
    Шифрует данное сообщение.

    :param public_key: открытый ключ
    :param message: сообщение
    :return: зашифрованное сообщение

    """
    message = bytes(message, 'utf-8')
    return rsa.encrypt(message, pub_key)


def decrypt(private_key, message):
    """
    Расшифровывает данное сообщение.

    :param private_key: закрытый ключ
    :param message: побитово закодированное сообщение
    :return: расшифрованное сообщение

    """
    message = rsa.decrypt(message, private_key)
    return message.decode('utf-8')


if __name__ == '__main__':
    (pub_key, priv_key) = gen_keys()
    print(pub_key)
    print(priv_key)

    msg = "Хуй с маслом."
    print(f'We want to send: "{msg}"')

    encrypted_msg = encrypt(pub_key, msg)
    print(f'Encrypted message: "{encrypted_msg}"')

    decrypted_msg = decrypt(priv_key, encrypted_msg)
    print(f'Decrypted message: "{decrypted_msg}"')
