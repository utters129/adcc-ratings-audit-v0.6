#!/usr/bin/env python3
"""
Generate secure secret keys for webhook and JWT
"""
import secrets
import string

def generate_webhook_secret():
    """Generate a secure webhook secret key"""
    # Generate 64 random characters (mix of letters, digits, and symbols)
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    # Generate 32 random bytes and encode as hex
    return secrets.token_hex(32)

if __name__ == "__main__":
    print("🔐 Generating secure secret keys...")
    print()
    
    webhook_secret = generate_webhook_secret()
    jwt_secret = generate_jwt_secret()
    
    print("📋 Copy these values to your Railway environment variables:")
    print()
    print(f"WEBHOOK_SECRET={webhook_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    print("⚠️  Keep these secrets secure and never share them!")
    print("💡 You can also use these in your local railway.env file") 