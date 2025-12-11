"""
Generate bcrypt salt for admin user seeding
This ensures consistent password hashing across environments
"""
import bcrypt


def generate_salt():
    """Generate a bcrypt salt"""
    salt = bcrypt.gensalt()
    return salt.decode('utf-8')


if __name__ == "__main__":
    salt = generate_salt()
    print("\n" + "="*60)
    print("Generated bcrypt salt for admin user:")
    print("="*60)
    print(f"\n{salt}\n")
    print("="*60)
    print("Add this to your .env file:")
    print("="*60)
    print(f"\nADMIN_PASSWORD_SALT={salt}\n")
    print("="*60)
    print("\nNote: Use the SAME salt in all environments (local, AWS)")
    print("to ensure consistent password hashing.")
    print("="*60 + "\n")
