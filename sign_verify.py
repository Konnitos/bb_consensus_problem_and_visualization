from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

key = RSA.generate(1024)

private_key = key.export_key()
public_key = key.public_key().export_key()

message = b"ATTACK!"
hash = SHA256.new(message)

signature = PKCS1_v1_5.new(RSA.import_key(private_key)).sign(hash)

print(PKCS1_v1_5.new(RSA.import_key(public_key)).verify(hash,signature))