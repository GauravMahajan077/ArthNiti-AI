import secrets
secret_key = secrets.token_urlsafe(50)  # Generates a 50-char URL-safe string (adjust length as needed)
print(secret_key)