import secrets

def generate_custom_random_unique_word(length=8):
    # Определяем собственный набор символов
    custom_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    # Или можно добавить специальные символы:
    # custom_characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    secure_random_string = ''.join(secrets.choice(custom_characters) for _ in range(length))
    return secure_random_string
