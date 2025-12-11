"""
Generate encryption key for artifact ID encryption
This key should be stored securely in environment variables
"""
import sys
import os

# Add parent directory to path to import lib
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from lib.encryption import generate_encryption_key  # noqa: E402


def main():
    """Generate and display a new encryption key"""
    key = generate_encryption_key()

    print("\n" + "="*60)
    print("Generated Encryption Key for Artifact IDs:")
    print("="*60)
    print(f"\n{key}\n")
    print("="*60)
    print("Add this to your .env file:")
    print("="*60)
    print(f"\nARTIFACT_ENCRYPTION_KEY={key}\n")
    print("="*60)
    print("\nIMPORTANT:")
    print("- Use the SAME key in all environments")
    print("  (local, Lambda, Fargate)")
    print("- Store this key securely")
    print("  (AWS Secrets Manager, SSM Parameter Store)")
    print("- NEVER commit this key to version control")
    print("- If compromised, generate a new key and re-encrypt")
    print("  all artifact IDs")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
