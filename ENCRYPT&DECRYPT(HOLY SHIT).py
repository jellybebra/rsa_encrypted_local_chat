import rsa #importim, bleyat
#generate keys(degenerate my psychopass)
(pub_key, priv_key) = rsa.newkeys(1024) #1024 - length of byts(Оказывается, там какая-то ахуенная закономерность, поэтому длина ключа должна быть больше длины самого сообщения, при том в значительное кол-во раз)
#ENFUCK & DEFUCK
#Я забыл как по-человечески фигачить рэйнжи, поэтому, да
message = b'Misha, pridumay cho s messeigem delat' #эта b - если забыл - обозначает, что эта хрень имеет дело именно с байтами, без неё всё крашится к хренам
crypto = rsa.encrypt(message, pub_key) #ENFUCK
print(crypto)
message = rsa.decrypt(crypto, priv_key) #DEFUCK
print(message)

