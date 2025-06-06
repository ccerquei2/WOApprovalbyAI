# encrypt.py

# Parte comentada utilizada para gerar a chave aleatória "ygXpEovWlhdviLtINXolxFknobzZWhwEEDkvFLt5_nY="
# from cryptography.fernet import Fernet
#
# key = Fernet.generate_key()
# print("Y/QZGmLTgAIN6efC9XRk3aqZfK/ISe01mwzDjszasrk=")
#
# print(key.decode())




from cryptography.fernet import Fernet

# Sua chave (copiada da etapa anterior)
key = b'ygXpEovWlhdviLtINXolxFknobzZWhwEEDkvFLt5_nY='
fernet = Fernet(key)

with open("secrets.yaml", "rb") as f:
    plaintext = f.read()

encrypted = fernet.encrypt(plaintext)

with open("secrets.enc", "wb") as f:
    f.write(encrypted)

print("Arquivo criptografado com sucesso.")
