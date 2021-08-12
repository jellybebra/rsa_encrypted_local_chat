recipient_pub_key = b'bruh'
answer = f'!ka '.encode('utf-8') + recipient_pub_key

ans_decoded = answer.decode('utf-8')
print(ans_decoded)  # !ka bruh

"""

Из-за этого могут быть баги. Типа bruh пришёл раскодированный.

"""


def encode_bytes(bytes: bytes) -> bytes:
    import base64
    return base64.b64encode(bytes)


def decode_bytes(bytes: bytes) -> bytes:
    import base64
    return base64.b64decode(bytes)
