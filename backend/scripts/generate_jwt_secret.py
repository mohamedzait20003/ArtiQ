"""
Generate JWT secret key for token signing
This key should be stored securely in environment variables
"""
import secrets


def generate_jwt_secret():
    """
    Generate a secure random JWT secret key
    
    Returns:
        str: A secure random 64-character hexadecimal string
    """
    # Generate 32 bytes (256 bits) of random data
    # This is converted to a 64-character hexadecimal string
    return secrets.token_hex(32)


if __name__ == "__main__":
    secret_key = generate_jwt_secret()
    
    print("\n" + "="*60)
    print("Generated JWT Secret Key for Token Signing:")
    print("="*60)
    print(f"\n{secret_key}\n")
    print("="*60)
    print("Add this to your .env file:")
    print("="*60)
    print(f"\nJWT_SECRET_KEY={secret_key}\n")
    print("="*60)
    print("\nIMPORTANT:")
    print("- Use the SAME key in all environments")
    print("  (local, Lambda, AWS)")
    print("- Store this key securely")
    print("  (AWS Secrets Manager, SSM Parameter Store)")
    print("- NEVER commit this key to version control")
    print("- If compromised, generate a new key")
    print("  (this will invalidate all existing tokens)")
    print("- Recommended key length: 256 bits (64 hex characters)")
    print("="*60 + "\n")
