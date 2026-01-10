#!/usr/bin/env python
"""
Helper script to add a valid HuggingFace token to the database.
Run this script to quickly add a valid token without using the web interface.

Usage:
    python add_valid_token.py <token> <name>

Example:
    python add_valid_token.py hf_xxxxxxxxxxxxx "Production Token"
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, HuggingFaceToken


def add_token(token_value, token_name):
    """Add a HuggingFace token to the database."""
    
    # Get admin user (or create one if doesn't exist)
    admin_user = User.objects.filter(role='admin').first()
    
    if not admin_user:
        print("ERROR: No admin user found!")
        print("Please create an admin user first or specify one.")
        return False
    
    # Check if token already exists
    if HuggingFaceToken.objects.filter(token=token_value).exists():
        print(f"ERROR: Token already exists in database!")
        return False
    
    # Create the token
    hf_token = HuggingFaceToken.objects.create(
        token=token_value,
        name=token_name,
        is_active=True,
        created_by=admin_user
    )
    
    print(f"✓ Successfully added HuggingFace token!")
    print(f"  ID: {hf_token.id}")
    print(f"  Name: {hf_token.name}")
    print(f"  Created by: {admin_user.username}")
    print(f"  Active: {hf_token.is_active}")
    
    return True


def delete_invalid_tokens():
    """Delete tokens that look invalid (too short or test tokens)."""
    invalid_tokens = HuggingFaceToken.objects.filter(
        token__in=['a', 'aa', 'test', 'your-huggingface-token-here']
    )
    
    count = invalid_tokens.count()
    if count > 0:
        print(f"\nFound {count} invalid test token(s). Deleting...")
        for token in invalid_tokens:
            print(f"  Deleting: {token.name} (token: {token.token})")
        invalid_tokens.delete()
        print(f"✓ Deleted {count} invalid token(s)")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nCurrent tokens in database:")
        tokens = HuggingFaceToken.objects.all()
        if tokens.exists():
            for token in tokens:
                print(f"  - {token.name}: {token.token[:10]}... (Active: {token.is_active})")
        else:
            print("  No tokens found")
        sys.exit(1)
    
    token = sys.argv[1]
    name = sys.argv[2]
    
    if not token.startswith('hf_'):
        print("WARNING: Token doesn't start with 'hf_'. Are you sure this is a valid HuggingFace token?")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Delete invalid tokens first
    delete_invalid_tokens()
    
    # Add the new token
    if add_token(token, name):
        print("\n✓ Done! You can now use the chat feature.")
    else:
        sys.exit(1)
