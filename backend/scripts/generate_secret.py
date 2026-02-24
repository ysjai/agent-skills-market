#!/usr/bin/env python3
"""Generate a secure SECRET_KEY for production."""

import secrets
import sys


def generate_secret():
    """Generate a secure random secret key."""
    key = secrets.token_hex(32)
    print(f"\n🔐 Generated SECRET_KEY:\n{key}\n")
    print("Add this to your .env file:")
    print(f"SECRET_KEY={key}")
    return key


def update_env_file():
    """Generate key and show instructions."""
    key = generate_secret()

    print("\n💡 To append to .env automatically:")
    print(f'  echo "SECRET_KEY={key}" >> .env')

    print("\n⚠️  Note: Make sure .env is in .gitignore!")

    return key


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--update", "-u"):
        update_env_file()
    else:
        generate_secret()
