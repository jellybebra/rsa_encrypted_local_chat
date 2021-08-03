import rsa #importim, bleyat
#Generate keys
(pub_key, priv_key) = rsa.newkeys(1024) #1024 - length of byts(I don't give a fuck if we need it or not)
#enfuck & defuck
message = b'Misha, pridumay cho s messeigem delat'
crypto = rsa.encrypt(message, pub_key) #ENFUCK
print(crypto)
message = rsa.decrypt(crypto, priv_key) #DEFUCK
print(message)

