# decrypt.py

from cryptography.fernet import Fernet
import yaml

def decrypt_keys(idkey):
    # Sua chave original
    key = b'ygXpEovWlhdviLtINXolxFknobzZWhwEEDkvFLt5_nY='
    fernet = Fernet(key)

    with open("secrets.enc", "rb") as f:
        encrypted = f.read()

    plaintext = fernet.decrypt(encrypted)
    secrets = yaml.safe_load(plaintext)

    # # Exemplo de uso:
    # print(secrets["openai_api_key"])
    # print(secrets["groq_api_key"])
    # print(secrets["username"])
    # print(secrets["password"])

    return secrets[idkey]
