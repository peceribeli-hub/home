#!/usr/bin/env python3
"""
Utilitário para gerar hash de senha
Uso: python generate_hash.py minha_senha
"""
import hashlib
import sys

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python generate_hash.py sua_senha")
        print("Exemplo: python generate_hash.py senha123")
        sys.exit(1)
    
    password = sys.argv[1]
    hash_value = hash_password(password)
    print(f"Senha: {password}")
    print(f"Hash: {hash_value}")
    print()
    print("Cole o hash no Vercel como CLIENT_X_PASSWORD_HASH")
