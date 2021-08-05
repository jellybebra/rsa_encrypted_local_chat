import socket
import threading

port = 8080
host = socket.gethostname()

s = socket.socket()
s.bind((host, port))  # двойные скобки потому, что это кортеж (tuple)
s.listen(1)
print(f"[SERVER] Listening on {host}.")
print("[SERVER] Waiting for incoming connections...")

conn, addr = s.accept()

name = input("Enter your username: ")

print("[SERVER] Waiting for another user to pass their name...")
second_name = conn.recv(1024).decode()
print(second_name, "has joined the chat room.")


def input_and_output():
    while 1:  # 1 - то же самое, что и True (т.е. всё, что внутри цикла, будет работать до конца
        msg = name + " : " + input(str("Please enter your message: "))
        conn.send(msg.encode())
        print("[] Sent. \n")


background_thread = threading.Thread(target=input_and_output)
background_thread.daemon = True  # вот. это то, что мне нужно было.
background_thread.start()

for message in iter(lambda: conn.recv(1024).decode(), ''):
    print(f'[{second_name}] {message} \n')
