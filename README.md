# rsa_encrypted_local_chat
 
# Цель
Два человека, подключенные к одной сети, открывают на своём устройстве одну и ту же программу. С одного компьютера передаём зашифрованный файл, содержащий 72 числовых значения. На другом компьютере этот файл должен быть получен и расшифрован. Необходимо использовать открытые и закрытые ключи.

# Как работает программа (версия 1)
1. Запущенная программа устанавливает наличие запущенного в сети сервера и, если такового нет, становится им, а в случае его присутствия - подключается к нему.
2. Сервер отправляет клиенту открытый ключ
3. Клиент зашифровывает сообщение данным открытым ключом и отправляет результат серверу

# Как работает программа (версия 2)
1. Запущенная программа устанавливает наличие запущенного в сети сервера и, если такового нет, становится им, а в случае его присутствия - подключается к нему.
2. Происходит обмен открытых ключей
3. Сервер и клиент обмениваются зашифрованными сообщениями

# Как работает шифрование (RSA)
1. Генерируются связанные между собой ключи: открытый (public) и закрытый (private).
2. Происходит обмен открытых ключей между пользователями
3. Пользователи шифруют свои сообщения полученными ключами собеседников и отправляют результаты
4. Пользователи расшифровывают полученные сообщения с помощью своих закрытых ключей.

Более подробно о данном шифровании можно узнать [здесь](http://www.michurin.net/computer-science/rsa.html).

# Какие-то заметки
How it is done in practice is that no one uses RSA to encrypt messages. They use RSA to encrypt (and sign) an encryption key, and then encrypt the message with the encryption key. They send the encrypted key and the encrypted message to the other party. The other party uses their RSA private key to decrypt the key, then uses that key to decrypt the message. Furthermore, in practice, they also add padding to the key before encrypting it with RSA.

Что-то про [прокладки](https://en.wikipedia.org/wiki/Padding_(cryptography)).

# Что-то про RSA
https://pypi.org/project/rsa/

https://stuvel.eu/python-rsa-doc/usage.html#generating-keys

https://youtu.be/rrKuqbTDom8

# Благодарности

[Как найти всех хостов в сети?](https://www.tutorialspoint.com/python_penetration_testing/python_penetration_testing_network_scanner.htm)

[Как сделать обмен сообщениями в локальной сети? Сокеты в Python.](https://youtu.be/3QiPPX-KeSc)

[Другая версия поиска всех хостов в сети с помощью nmap.](https://youtu.be/FrT_n5BkpK4)

# Похожие проекты
https://github.com/sathwikv143/Encrypted-Python-Chat
